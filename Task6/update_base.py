import hashlib
import json
import logging
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================
KB_DIR = Path("../Task2/knowledge_base")           # основная база знаний
INCOMING_DIR = Path("incoming")                    # буферная папка для новых файлов
ARCHIVE_DIR = INCOMING_DIR / "archive"             # архив невалидных/дубликатов
INDEX_PATH = Path("../Task3/faiss_index")          # FAISS-индекс в Task3
MANIFEST_PATH = Path("manifest.json")              # хеши файлов
LOG_PATH = Path("update.log")                      # общий лог

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ============================================================
# ЛОГИРОВАНИЕ
# ============================================================
logger = logging.getLogger("update_base")
logger.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

_file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
_file_handler.setFormatter(_formatter)
logger.addHandler(_file_handler)

_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setFormatter(_formatter)
logger.addHandler(_stream_handler)


# ============================================================
# УТИЛИТЫ: ХЕШИ, МАНИФЕСТ
# ============================================================
def file_md5(path: Path) -> str:
    """Возвращает MD5-хеш содержимого файла."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> Dict[str, str]:
    """Загружает manifest.json (имя файла -> MD5)."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(manifest: Dict[str, str]) -> None:
    """Сохраняет manifest.json."""
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def detect_changes(kb_dir: Path, manifest: Dict[str, str]) -> List[Path]:
    """Возвращает список новых или изменённых файлов в knowledge_base/."""
    changed: List[Path] = []
    if not kb_dir.exists():
        return changed
    for file_path in sorted(kb_dir.glob("*.md")):
        if manifest.get(file_path.name) != file_md5(file_path):
            changed.append(file_path)
    return changed


# ============================================================
# УТИЛИТЫ: ИМЕНА, ВАЛИДАЦИЯ, ДУБЛИКАТЫ
# ============================================================
_TRANSLIT_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
}


def slugify(name: str) -> str:
    """Преобразует имя файла в безопасный slug (латиница, цифры, _, -)."""
    stem = Path(name).stem
    suffix = Path(name).suffix
    translit = "".join(_TRANSLIT_MAP.get(ch, ch) for ch in stem)
    slug = re.sub(r"[^A-Za-z0-9_\-]+", "_", translit)
    slug = re.sub(r"_+", "_", slug).strip("_") or "document"
    return slug + suffix


def next_index(kb_dir: Path) -> int:
    """Возвращает следующий свободный числовой префикс для имени файла."""
    max_n = 0
    if not kb_dir.exists():
        return 1
    for f in kb_dir.glob("*.md"):
        m = re.match(r"^(\d+)_", f.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n + 1


def validate_file(path: Path) -> Tuple[bool, str]:
    """Проверяет, что файл является .md, не пустой и в UTF-8."""
    if path.suffix.lower() != ".md":
        return False, f"пропущен (не .md): {path.name}"
    if path.stat().st_size == 0:
        return False, f"пропущен (пустой): {path.name}"
    try:
        path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, f"пропущен (не UTF-8): {path.name}"
    return True, "ok"


def is_duplicate_by_hash(path: Path, manifest: Dict[str, str]) -> bool:
    """Проверяет, есть ли файл с таким же MD5 в knowledge_base/."""
    h = file_md5(path)
    return h in manifest.values()


# ============================================================
# ИНКРЕМЕНТАЛЬНОЕ ОБНОВЛЕНИЕ FAISS-ИНДЕКСА
# ============================================================
def update_index() -> None:
    """Инкрементально обновляет FAISS-индекс по MD5-манифесту."""
    start_time = time.time()
    logger.info("-" * 60)
    logger.info(f"🔄 Обновление векторного индекса по пути {INDEX_PATH}")

    if not KB_DIR.exists():
        logger.error(f"❌ Папка {KB_DIR} не найдена. Обновление индекса прервано.")
        return

    manifest = load_manifest()
    logger.info(f"📋 Manifest: {len(manifest)} записей")

    changed_files = detect_changes(KB_DIR, manifest)
    if not changed_files:
        logger.info("✅ Нет новых или изменённых файлов. Индекс не обновлялся.")
        return

    logger.info(f"🆕 Новых/изменённых файлов: {len(changed_files)}")
    for f in changed_files:
        logger.info(f"   - {f.name}")

    # 1. Загрузка документов
    documents = []
    for file_path in changed_files:
        loader = TextLoader(str(file_path), encoding="utf-8")
        documents.extend(loader.load())

    # 2. Чанкинг
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"✂️ Чанков получено: {len(chunks)}")

    # 3. Эмбеддинги
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    # 4. Инкрементальное обновление FAISS в ../Task3/faiss_index
    if INDEX_PATH.exists():
        logger.info(f"📂 Загрузка существующего индекса из {INDEX_PATH}")
        vectorstore = FAISS.load_local(
            str(INDEX_PATH),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        vectorstore.add_documents(chunks)
    else:
        logger.info(f"📂 Индекс не найден — создаётся новый в {INDEX_PATH}")
        INDEX_PATH.mkdir(parents=True, exist_ok=True)
        vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(str(INDEX_PATH))
    logger.info(f"💾 Индекс сохранён в {INDEX_PATH}")

    # 5. Обновление манифеста
    for file_path in changed_files:
        manifest[file_path.name] = file_md5(file_path)
    save_manifest(manifest)
    logger.info(f"📝 Manifest обновлён ({len(manifest)} записей)")

    elapsed = time.time() - start_time
    logger.info(
        f"✅ Индекс обновлён: файлов={len(changed_files)}, "
        f"чанков={len(chunks)}, время={elapsed:.2f} сек."
    )
    logger.info("-" * 60)


# ============================================================
# ПРИЁМ НОВЫХ ФАЙЛОВ ИЗ incoming/
# ============================================================
def process_incoming() -> List[Path]:
    """Обрабатывает incoming/: валидация, slugify, дедупликация, перенос в KB."""
    if not INCOMING_DIR.exists():
        logger.warning(f"📁 Папка {INCOMING_DIR}/ не найдена. Пропускаем приём.")
        return []

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    KB_DIR.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest()
    moved: List[Path] = []

    incoming_files = sorted(INCOMING_DIR.glob("*.md"))
    if not incoming_files:
        logger.info("📭 Папка incoming/ пуста. Новых файлов нет.")
        return []

    logger.info(f"📥 Найдено файлов в incoming/: {len(incoming_files)}")
    n = next_index(KB_DIR)

    for src in incoming_files:
        # 1. Валидация
        ok, msg = validate_file(src)
        if not ok:
            logger.warning(f"   ⚠️ {msg} → archive/")
            shutil.move(str(src), str(ARCHIVE_DIR / src.name))
            continue

        # 2. Дубликат по MD5
        if is_duplicate_by_hash(src, manifest):
            logger.warning(f"   ♻️ Дубликат по содержимому: {src.name} → archive/")
            shutil.move(str(src), str(ARCHIVE_DIR / src.name))
            continue

        # 3. Нормализация имени + префикс
        slug = slugify(src.name)
        dst = KB_DIR / f"{n:02d}_{slug}"
        counter = 1
        while dst.exists():
            dst = KB_DIR / f"{n:02d}_{Path(slug).stem}_{counter}.md"
            counter += 1

        # 4. Перенос
        shutil.move(str(src), str(dst))
        logger.info(f"   ✅ {src.name} → {dst.name}")
        moved.append(dst)
        n += 1

    return moved


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================
def update_base() -> None:
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("🚀 Запуск update_base.py")

    moved = process_incoming()
    if not moved:
        logger.info("📭 Новых файлов не принято. Проверяем изменения в knowledge_base/...")

    try:
        update_index()
    except Exception as e:
        logger.exception(f"❌ Ошибка при обновлении индекса: {e}")
        raise

    elapsed = time.time() - start_time
    logger.info(f"🏁 Готово за {elapsed:.2f} сек. Принято файлов: {len(moved)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        update_base()
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка: {e}")
        sys.exit(1)