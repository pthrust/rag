import json
import sys
from pathlib import Path
from typing import List, Dict

# Импортируем функции бота
sys.path.insert(0, str(Path("../Task4").resolve()))
sys.path.insert(0, str(Path(".").resolve()))

from rag_bot import ask, retriever
from logger import log_query, is_successful_answer

GOLDEN_PATH = Path("golden_questions.txt")
REPORT_PATH = Path("evaluation_report.json")


def parse_golden(path: Path) -> List[Dict]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue

        if line.encode('utf8').startswith(b"\xEF\xbb\xbf#"):
            continue

        if line.startswith("#"):
            continue


        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue

        items.append({
            "question": parts[0],
            "expected": parts[1],
            "keywords": parts[2].split(",") if parts[2] != "—" else [],
        })
    return items


def evaluate() -> Dict:
    items = parse_golden(GOLDEN_PATH)
    print(f"📋 Загружено вопросов: {len(items)}\n")

    results = []
    tp = fp = tn = fn = 0

    for i, item in enumerate(items, 1):
        q = item["question"]

        expected = item["expected"]
        print(f"[{i}/{len(items)}] Q: {q}")

        # Получаем чанки + similarity scores
        docs_with_scores = retriever.vectorstore.similarity_search_with_score(q, k=5)
        chunks = [d.page_content for d, _ in docs_with_scores]
        sources = [d.metadata.get("source", "unknown") for d, _ in docs_with_scores]
        scores = [s for _, s in docs_with_scores]

        answer = ask(q)
        success = is_successful_answer(answer, chunks)

        # Проверка ключевых слов (только для expected=answer)
        keyword_hit = True
        if expected == "answer" and item["keywords"]:
            lower = answer.lower()
            keyword_hit = any(kw.strip().lower() in lower for kw in item["keywords"])

        # Логирование
        log_query(q, chunks, sources, answer, success, extra=None) # extra=scores

        # Классификация
        if expected == "answer" and success and keyword_hit:
            tp += 1
            verdict = "✅ OK"
        elif expected == "answer" and (not success or not keyword_hit):
            fn += 1
            verdict = "❌ MISS (не ответил или не упомянул ключевые слова)"
        elif expected == "no_answer" and not success:
            tn += 1
            verdict = "✅ OK (честно сказал 'не знаю')"
        else:
            fp += 1
            verdict = "⚠️ FALSE POSITIVE (галлюцинация)"

        print(f"   → {verdict} | chunks={len(chunks)}, "
              f"len={len(answer)}, scores={[round(s,3) for s in scores[:2]]}\n")

        results.append({
            "question": q,
            "expected": expected,
            "success": success,
            "keyword_hit": keyword_hit,
            "chunks_found": len(chunks),
            "sources": sources,
            "similarity_scores": [round(s, 4) for s in scores],
            "answer_preview": answer[:200],
            "verdict": verdict,
        })

    total = len(items)
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    print("=" * 60)
    print("📊 Метрики:")
    print(f"   Accuracy:  {accuracy:.3f}")
    print(f"   Precision: {precision:.3f}")
    print(f"   Recall:    {recall:.3f}")
    print(f"   F1-score:  {f1:.3f}")
    print(f"   TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    return report


if __name__ == "__main__":
    evaluate()