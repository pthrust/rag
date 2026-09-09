import os
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

llm = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0.0,
    base_url=OLLAMA_BASE_URL,
    num_predict=512,          # ограничение длины ответа
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
    """
    Собирает список сообщений для ChatOllama:
      - SystemMessage с инструкцией,
      - Few-shot примеры в виде диалога,
      - HumanMessage с контекстом и вопросом.
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Добавляем few-shot примеры
    for ex in FEW_SHOT_EXAMPLES:
        messages.append(HumanMessage(content=ex["question"]))
        messages.append(AIMessage(content=ex["answer"]))

    # Формируем контекст
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

def ask(question: str) -> str:
    """Основная функция: принимает вопрос, возвращает ответ."""
    chunks = retrieve_context(question)
    if not chunks:
        return "Я не знаю (в базе нет релевантных документов)."

    messages = build_prompt(question, chunks)
    response = llm.invoke(messages)
    return response.content

# ===== Консольный режим =====
if __name__ == "__main__":
    print("🚀 RAG-бот (Llama-3.1-8B) запущен. Введите 'exit' для выхода.")
    while True:
        q = input("\nВаш вопрос: ")
        if q.lower() in ("exit", "quit", "q"):
            break
        answer = ask(q)
        print("\nОтвет бота:\n", answer)