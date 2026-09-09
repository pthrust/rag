# Создание векторного индекса базы знаний

## 1. Выбор модели эмбеддингов

В соответствии с решением, принятым для реализации MVP в Задании 1, для индексации будет использоваться локальная модель эмбеддингов:

- **Название:** all-MiniLM-L6-v2 (Sentence‑Transformers)  
- **Репозиторий:** sentence-transformers/all-MiniLM-L6-v2  
- **Размерность:** 384 (быстрый и компактный вариант, обеспечивающий достаточное качество для MVP)  
- **Преимущества:** работает без интернета, бесплатна, легко развёртывается, не требует GPU.  

Модель загружается через библиотеку langchain_community.embeddings.HuggingFaceEmbeddings.

## 2. Подготовка окружения для генерации векторного индекса

```
python -m venv ~/rag
source ~/rag/bin/activate
pip install langchain langchain-ollama langchain-huggingface langchain-community faiss-cpu sentence-transformers
python build_index.py

[+] Loading documents from knowledge_base/ ...
[+] Loaded 35 documents.
[+] Splitting into chunks...
[+] Obtained 35 chunks.
[+] Generating embeddings (model all-MiniLM-L6-v2)...
[+] Creating and saving FAISS index...
[+] Index saved to faiss_index/
  Indexing time: 0.88 sec.
  Total chunks: 35
  Done!
```

## 3. Пример запроса к индексу

Сам скрипт уже содержит тестовый поиск. Ниже приведён ожидаемый вывод для запроса «Кто уничтожил Void Engine?» (основан на реальных данных базы знаний):

```
[+] Test search for query: Who destroyed the Void Engine?

--- Result 1 (score: 0.5468) ---
Source: ../Task2/knowledge_base/20_Void_Engine.md
Text: Void Engine — a superweapon of Imperium, a moon‑sized station. Can destroy entire planets with a focused energy beam. Its only weakness is the thermal reactor, accessible through a narrow exhaust tunn...

--- Result 2 (score: 0.8969) ---
Source: ../Task2/knowledge_base/32_Assault_on_Jungle_Haven.md
Text: The first major victory of the Freedom Coalition. Using small‑craft tactics, the rebels destroyed the Void Engine. Orin Lightseeker, piloting an Aegis Strike Fighter, launched a torpedo into the therm...

--- Result 3 (score: 0.9338) ---
Source: ../Task2/knowledge_base/03_Orin_Lightseeker.md
Text: Orin Lightseeker — a young farmer from Dustfall who later became a key figure of the Freedom Coalition. He destroyed the Void Engine using Aetherium and his piloting skills in an Aegis Strike Fighter....
```

### Провекрка 

**The Void Engine** - это Death Star уничтожена Люком Скайуокером. В данном котексте данный персонаж именнуется **Orin Lightseeker** и последний выввод результата со score 0.9338 соответствует истине в ново-созданной индексной базе 