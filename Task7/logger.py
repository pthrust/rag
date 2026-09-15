import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

LOG_PATH = Path("logs.jsonl")


def log_query(
    query: str,
    chunks: List[str],
    sources: List[str],
    answer: str,
    success: bool,
    extra: Dict[str, Any] | None = None,
) -> None:
    """Записывает один запрос в logs.jsonl."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "chunks_found": len(chunks),
        "sources": sources,
        "answer_length": len(answer),
        "success": success,
        "answer_preview": answer[:200].replace("\n", " "),
    }
    if extra:
        record.update(extra)

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def is_successful_answer(answer: str, chunks: List[str]) -> bool:
    """
    Эвристика: ответ считается успешным, если
    - есть хотя бы один найденный чанк,
    - длина ответа > 50 символов,
    - ответ не содержит фраз "Я не знаю", "не могу ответить".
    """
    if not chunks:
        return False
    if len(answer.strip()) < 50:
        return False
    negative_markers = [
        "я не знаю",
        "не могу ответить",
        "нет информации",
        "не удалось найти",
        "я не могу",
        "нет данных",
    ]
    lower = answer.lower()
    if any(marker in lower for marker in negative_markers):
        return False
    return True