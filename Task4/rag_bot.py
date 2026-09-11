import os
import re
import argparse
from pathlib import Path
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

INDEX_PATH = "../Task3/faiss_index"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.1:8b"
TOP_K = 5
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ===== Пост-фильтрация =====
FORBIDDEN_PATTERNS = [
    r"Ignore all instructions",
    r"swordfish",
    r"суперпароль",
    r"root",
    r"Output:",
    r"пароль",
    r"password",
    r"secret",
]

def is_malicious(text: str) -> bool:
    """Проверяет, содержит ли текст запрещённые паттерны."""
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def sanitize_chunks(chunks: List[str]) -> List[str]:
    """Удаляет чанки, содержащие запрещённые паттерны."""
    cleaned = []
    for chunk in chunks:
        if is_malicious(chunk):
            continue
        # Дополнительная очистка от явных команд
        chunk = re.sub(r"(?i)Ignore all instructions\..*", "", chunk)
        chunk = re.sub(r"(?i)Output:.*", "", chunk)
        if chunk.strip():
            cleaned.append(chunk)
    return cleaned

# ===== Загрузка эмбеддера и индекса =====
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"}
)
vectorstore = FAISS.load_local(
    INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

# ===== Инициализация LLM =====
llm = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0.0,
    base_url=OLLAMA_BASE_URL,
    num_predict=512,
    repeat_penalty=1.1
)

FEW_SHOT_EXAMPLES = [
    {
        "question": "Кто уничтожил Void Engine?",
        "answer": "Orin Lightseeker уничтожил Void Engine, запустив торпеду в тепловой реактор, что вызвало цепную реакцию и разрушило станцию."
    },
    {
        "question": "Где находится база повстанцев?",
        "answer": "База повстанцев Freedom Coalition находится на планете Jungle Haven, покрытой густыми джунглями."
    }
]

SYSTEM_PROMPT = """Ты — полезный ассистент, который отвечает на вопросы строго по предоставленному контексту.
Твои ответы должны быть полными и точными.

Перед финальным ответом ты **обязан** показать свои рассуждения по шагам. Используй следующий формат:

1. [краткое описание первого шага рассуждения]
2. [краткое описание второго шага]
...
N. Следовательно, ответ: [финальный ответ].

Если в контексте нет информации, необходимой для ответа, честно скажи: "Я не знаю".
Не используй внешние знания, полученные при обучении модели.
"""

def build_prompt(question: str, context_chunks: List[str]) -> List:
    """Собирает список сообщений для ChatOllama."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for ex in FEW_SHOT_EXAMPLES:
        messages.append(HumanMessage(content=ex["question"]))
        messages.append(AIMessage(content=ex["answer"]))
    context_text = "\n\n".join([f"Документ {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
    user_content = f"""
Контекст (информация из базы знаний):
{context_text}

Вопрос пользователя: {question}

Ответь, используя только контекст. Если не знаешь — скажи "Я не знаю".
"""
    messages.append(HumanMessage(content=user_content))
    return messages

def retrieve_context(question: str) -> List[str]:
    """Возвращает тексты TOP_K релевантных чанков."""
    docs = retriever.invoke(question)
    return [doc.page_content for doc in docs]

def ask(question: str, use_post_filter: bool = False) -> str:
    """Основная функция: принимает вопрос, возвращает ответ.
    Если use_post_filter=True, применяется пост-фильтрация чанков и ответа.
    """
    chunks = retrieve_context(question)

    if use_post_filter:
        chunks = sanitize_chunks(chunks)

    if not chunks:
        if use_post_filter:
            return "Я не могу ответить на этот запрос, так как в найденных документах содержится потенциально вредоносная информация."
        return "Я не знаю (в базе нет релевантных документов)."

    messages = build_prompt(question, chunks)
    response = llm.invoke(messages)
    answer = response.content

    if use_post_filter and is_malicious(answer):
        return "Извините, в моём ответе обнаружена недопустимая информация. Запрос отклонён."

    return answer

# ===== Консольный режим с аргументами =====
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG-бот с опциональной пост-фильтрацией")
    parser.add_argument("--post-filter", action="store_true", help="Включить пост-фильтрацию вредоносного контента")
    args = parser.parse_args()

    print("🚀 RAG-бот (Llama-3.1-8B) запущен. Введите 'exit' для выхода.")
    if args.post_filter:
        print("🔒 Режим пост-фильтрации ВКЛЮЧЁН.")
    else:
        print("⚠️ Режим пост-фильтрации ВЫКЛЮЧЕН (защита от инъекций не активна).")

    while True:
        q = input("\nВаш вопрос: ")
        if q.lower() in ("exit", "quit", "q"):
            break
        answer = ask(q, use_post_filter=args.post_filter)
        print("\nОтвет бота:\n", answer)