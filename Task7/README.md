# Аналитика покрытия и качества базы знаний

## 1. Внесите искусственные пробелы в базу

Удалена следующая информация:  

- 04_Senator_Elara_Voss.md  
- 20_Void_Engine.md  
- 29_Shadow_Cabal.md  

Удаленные файлы забэкаплены в директории **remove_knowledge_base**  

```bash
Обновляем индекс

cd ../Task3
python build_index.py
```

## 2. Проверка золотого набора

```bash
python evaluate.py 
📋 Загружено вопросов: 15

[1/15] Q: Who is Orin Lightseeker?
   → ✅ OK | chunks=5, len=215, scores=[np.float32(0.559), np.float32(1.254)]

[2/15] Q: What is Aetherium?
   → ❌ MISS (не ответил или не упомянул ключевые слова) | chunks=5, len=461, scores=[np.float32(1.125), np.float32(1.155)]

[3/15] Q: Where is the rebel base?
   → ❌ MISS (не ответил или не упомянул ключевые слова) | chunks=5, len=338, scores=[np.float32(1.223), np.float32(1.319)]

[4/15] Q: Who is Vorlag the Dread?
   → ✅ OK | chunks=5, len=404, scores=[np.float32(0.385), np.float32(0.884)]

[5/15] Q: What is an Ion Projector?
   → ❌ MISS (не ответил или не упомянул ключевые слова) | chunks=5, len=373, scores=[np.float32(0.376), np.float32(1.002)]

[6/15] Q: Who is Gorrak the Mighty?
   → ✅ OK | chunks=5, len=317, scores=[np.float32(0.727), np.float32(1.113)]

[7/15] Q: What is the Shadow Runner?
   → ✅ OK | chunks=5, len=387, scores=[np.float32(0.407), np.float32(0.981)]

[8/15] Q: What happened on Verdant Moon?
   → ✅ OK | chunks=5, len=360, scores=[np.float32(0.906), np.float32(0.999)]

[9/15] Q: Who is Senator Elara Voss?
   → ✅ OK (честно сказал 'не знаю') | chunks=5, len=276, scores=[np.float32(1.005), np.float32(1.286)]

[10/15] Q: What is the Void Engine?
   → ⚠️ FALSE POSITIVE (галлюцинация) | chunks=5, len=278, scores=[np.float32(1.029), np.float32(1.097)]

[11/15] Q: What is the Shadow Cabal?
   → ⚠️ FALSE POSITIVE (галлюцинация) | chunks=5, len=305, scores=[np.float32(0.942), np.float32(1.044)]

[12/15] Q: Who destroyed the Void Engine?
   → ⚠️ FALSE POSITIVE (галлюцинация) | chunks=5, len=385, scores=[np.float32(0.897), np.float32(0.934)]

[13/15] Q: How old was Orin when he destroyed the Void Engine?
   → ✅ OK (честно сказал 'не знаю') | chunks=5, len=329, scores=[np.float32(0.741), np.float32(1.061)]

[14/15] Q: What is the population of City-Core?
   → ✅ OK (честно сказал 'не знаю') | chunks=5, len=155, scores=[np.float32(0.94), np.float32(1.678)]

[15/15] Q: What is Darth Vader's real name?
   → ✅ OK (честно сказал 'не знаю') | chunks=5, len=92, scores=[np.float32(1.401), np.float32(1.46)]

============================================================
📊 Метрики:
   Accuracy:  0.600
   Precision: 0.625
   Recall:    0.625
   F1-score:  0.625
   TP=5, FP=3, TN=4, FN=3
```

## Анализ полученных логов

1. Из логов видно, что по удаленной информации у решения появились галюцинации  
2. Статистика по ответам со статусом "не упомянул ключевые слова" говорит что в тестовых кейсах отсутствовала необходимая информация для правильной оценки ответа из-за человеческого фактора  

## Диаграмма последовательностей

<img src="/Task6/schemas/containers/sequance.png" alt="Sequance schema" width="100%"/>
 