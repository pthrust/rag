# Архитектура пайплайна для консольного rag-бота

```
Пользовательский запрос
        ↓
[1] Генерация эмбеддинга запроса (та же модель, что и при индексации)
        ↓
[2] Поиск ближайших чанков в FAISS (k=5)
        ↓
[3] Формирование промпта:
    - System: инструкция с CoT
    - Few-shot примеры (2 примера)
    - Контекст (найденные чанки)
    - Вопрос пользователя
        ↓
[4] Отправка промпта в LLM (ollama)
        ↓
[5] Парсинг и возврат ответа
```

# Подготовка docker с ollama

```
docker compose up

[+] up 9/9
 ✔ Image ollama/ollama:latest Pulled                                                                                                                                              236.4s
 ✔ Network task4_default      Created                                                                                                                                               0.1s
 ✔ Volume task4_ollama        Created                                                                                                                                               0.0s
 ✔ Container ollama           Created                                                                                                                                               0.5s
 ✔ Container model-puller     Created                                                                                                                                               0.1s
Attaching to model-puller, ollama
Container ollama Waiting 

Container ollama Healthy 
model-puller  | Pulling model: llama3.1:8b
...
model-puller  | Ollama is ready
...
ollama        | time=2026-09-09T15:38:11.101Z level=INFO source=download.go:181 msg="downloading 667b0c1932bc in 16 307 MB part(s)"
pulling manifest 
...
model-puller  | pulling 667b0c1932bc:  32% █████             1.6 GB/4.9 GB   20 MB/s   2m42s
...
model-puller  | pulling 667b0c1932bc: 100% █████████████████ 4.9 GB/4.9 GB   19 MB/s      0s
model-puller  | verifying sha256 digest 
model-puller  | writing manifest 
model-puller  | success 
model-puller  | Model llama3.1:8b pulled successfully
```
# Проверка ollama

```
docker exec -it ollama /bin/bash

root@4a57a5890226:/# who
root@4a57a5890226:/# ollama list
NAME           ID              SIZE      MODIFIED       
llama3.1:8b    46e0c10c039e    4.9 GB    14 minutes ago    

```

# Запуска бота + результаты ответов

```
python rag_bot.py

🚀 RAG-бот (Llama-3.1-8B) запущен. Введите 'exit' для выхода.

Ваш вопрос: Who is Anakin Skywalker

Ответ бота:
 Я не знаю. В предоставленном контексте нет упоминания о персонаже по имени Анакине Скиблоне.

Ваш вопрос: Who is Kaelen Stormrider

Ответ бота:
 1. В документе 1 упоминается, что Кэлен Стормрайдер был могучим Луминарием.
2. Он известен своим мастерством Атерия.
3. Он родился на планете Пыльная Падь (Dustfall).
4. Он был рабом, но позже стал героем Свободного Союза.

Следовательно, ответ: Кэлен Стормрайдер — могучий Луминарий.

Ваш вопрос: captain of Shadow Runner

Ответ бота:
 1. В документе 1 упоминается, что Rylan Stark является капитаном корабля Shadow Runner.
2. В документе 2 подтверждается, что Shadow Runner принадлежит Райлану Старку.

Следовательно, ответ: Райлан Старк.

Ваш вопрос: Where is finall battle

Ответ бота:
 1. В документе 1 упоминается "The final battle on Verdant Moon", что указывает на то, где произошла последняя битва.
2. Следовательно, ответ: Вердант Месяц.

Ваш вопрос: What is Endor

Ответ бота:
 1. В документе 3 упоминается планета Dustfall.
2. В документе 4 упоминается, что после уничтожения Void Engine Orin Lightseeker тренировал новую генерацию Луминари и отказался власти, чтобы странствовать по галактике.
3. Планеты, на которых находятся базы повстанцев (Jungle Haven) и где находится Дустфолл не указаны в документах как одинаковое место.

Следовательно, ответ: "Я не знаю".

Ваш вопрос: who attacks Glacier

Ответ бота:
 1. В документе 1 упоминается, что Imperium нашли базу повстанцев на планете Glacier с помощью проб.
2. В документе 2 говорится, что после обнаружения базы Imperium атаковали ее и уничтожили в ходе Glacier Siege.

Следовательно, ответ: Империя.
```

# Запуска бота + post фильтрация + результаты ответов

```bash
python rag_bot.py --post-filter


```
