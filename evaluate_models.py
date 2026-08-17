import os
os.environ["HF_HOME"] = "D:\\huggingface"

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import re

# ============================================================
# 1) LOAD DOCUMENTS DATA (for text and metadata)
# ============================================================

with open("documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

print("عدد الـDocuments:", len(documents))

# ============================================================
# 2) LOAD EMBEDDINGS HELPER
# ============================================================

def load_embeddings(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    doc_embs = np.array([item["embedding"] for item in data])
    source_ids = [item["source_id"] for item in data]
    titles = [item["title"] for item in data]
    texts = [item["text"] for item in data]
    return doc_embs, source_ids, titles, texts

# ============================================================
# 3) IMPORTANT WORDS (same as retrieval_tuning.py)
# ============================================================

def important_words(text):
    text = text.lower()
    words = re.findall(r"[a-z]+(?:-[a-z]+)?", text)
    stop_words = {
        "what", "are", "the", "for", "with",
        "and", "over", "years", "is", "in",
        "recommended", "should", "be", "to",
        "of", "a", "an", "when", "who"
    }
    return set(word for word in words if word not in stop_words)

# ============================================================
# 4) EVALUATION QUESTIONS (FIXED gold IDs)
# ============================================================

test_cases = [
    {
        "question": "What is a lower urinary tract infection?",
        "expected": "1.1.1"
    },
    {
        "question": "What advice should be given to all people with lower UTI about managing symptoms?",
        "expected": "1.1.2"
    },
    {
        "question": "What should be done if symptoms do not start to improve within 48 hours or worsen at any time for women with lower UTI who are not pregnant?",
        "expected": "1.1.3"
    },
    {
        "question": "What should be done when microbiological results are available after a urine sample was sent for culture and susceptibility testing?",
        "expected": "1.1.4"
    },
    {
        "question": "What should be done for pregnant women and men with lower UTI?",
        "expected": "1.1.5"
    },
    {
        "question": "What should people with lower UTI be advised to use for pain?",
        "expected": "1.3.1"
    },
    {
        "question": "What should be considered when prescribing antibiotics for lower UTI?",
        "expected": "1.4.1"
    },
    {
        "question": "What antibiotics are recommended for non-pregnant women aged 16 years and over?",
        "expected": "TABLE_1"
    },
    {
        "question": "What antibiotics are recommended for pregnant women aged 12 years and over?",
        "expected": "TABLE_2"
    },
    {
        "question": "What antibiotics are recommended for men aged 16 years and over?",
        "expected": "TABLE_3"
    },
    {
        "question": "What antibiotics are recommended for children and young people under 16 years?",
        "expected": "TABLE_4"
    }
]

questions = [case["question"] for case in test_cases]

# ============================================================
# 5) HYBRID SEARCH EVALUATION
# ============================================================

def evaluate_model(model_name, embeddings_file):
    print(f"\nتقييم {model_name} ...")

    doc_embs, source_ids, titles, texts = load_embeddings(embeddings_file)

    model = SentenceTransformer(model_name)
    query_embs = model.encode(questions)

    gold_ranks = []

    for i, case in enumerate(test_cases):
        query_emb = query_embs[i]

        # Compute L2 distances to all documents
        distances = np.sum((doc_embs - query_emb) ** 2, axis=1)

        # Get top 10 candidates by distance
        top10_indices = np.argsort(distances)[:10]

        # Hybrid scoring (same as retrieval_tuning.py)
        query_words = important_words(case["question"])
        scored = []

        for idx in top10_indices:
            title = titles[idx].lower()
            text = texts[idx].lower()

            title_words = important_words(title)
            text_words = important_words(text)

            title_matches = len(query_words & title_words)
            text_matches = len(query_words & text_words)

            semantic_score = 1 / (1 + distances[idx])
            hybrid_score = (
                semantic_score
                + (title_matches * 0.30)
                + (text_matches * 0.05)
            )

            scored.append({
                "id": source_ids[idx],
                "hybrid_score": hybrid_score,
                "distance": distances[idx],
                "title_matches": title_matches,
                "text_matches": text_matches
            })

        scored.sort(key=lambda x: x["hybrid_score"], reverse=True)
        top5_ids = [x["id"] for x in scored[:5]]

        if case["expected"] in top5_ids:
            rank = top5_ids.index(case["expected"]) + 1
            gold_ranks.append(rank)
        else:
            gold_ranks.append(None)

    found = sum(1 for r in gold_ranks if r is not None)
    recall_at_5 = found / len(test_cases)
    mrr = sum(1 / r for r in gold_ranks if r is not None) / len(test_cases)

    print(f"Recall@5: {recall_at_5:.4f} | MRR: {mrr:.4f}")

    return {
        "model": model_name,
        "recall": recall_at_5,
        "mrr": mrr,
        "file": embeddings_file
    }

# ============================================================
# 6) RUN EVALUATION
# ============================================================

MODELS = [
    ("all-MiniLM-L6-v2", "embeddings_model_1.json"),
    ("all-mpnet-base-v2", "embeddings_model_2.json"),
    ("paraphrase-multilingual-MiniLM-L12-v2", "embeddings_model_3.json"),
]

results = []

for model_name, embeddings_file in MODELS:
    res = evaluate_model(model_name, embeddings_file)
    results.append(res)

# ============================================================
# 7) PRINT COMPARISON TABLE
# ============================================================

print("\nEmbedding Model Comparison")
print("-" * 80)
print(f"{'Model':<45} {'Recall@5':<12} {'MRR':<12}")
print("-" * 80)

for res in results:
    print(
        f"{res['model']:<45} "
        f"{res['recall']:<12.4f} "
        f"{res['mrr']:<12.4f}"
    )

print("-" * 80)

best = max(results, key=lambda x: (x["recall"], x["mrr"]))
print(f"Best Model: {best['model']}")
