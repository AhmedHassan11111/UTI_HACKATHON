import os
os.environ["HF_HOME"] = "D:\\huggingface"

import json
import numpy as np
from sentence_transformers import SentenceTransformer

# ============================================================
# 1) LOAD DOCUMENTS
# ============================================================

with open("documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

print("عدد الـDocuments:", len(documents))

texts = [doc["text"] for doc in documents]
source_ids = [doc["source_id"] for doc in documents]

# ============================================================
# 2) MODELS TO COMPARE
# ============================================================

MODELS = [
    ("all-MiniLM-L6-v2", "embeddings_model_1.json"),
    ("all-mpnet-base-v2", "embeddings_model_2.json"),
    ("paraphrase-multilingual-MiniLM-L12-v2", "embeddings_model_3.json"),
]

# ============================================================
# 3) CREATE AND SAVE EMBEDDINGS
# ============================================================

for model_name, output_file in MODELS:

    print(f"\nجاري إنشاء Embeddings لـ {model_name} ...")

    model = SentenceTransformer(model_name)

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings_list = embeddings.tolist()

    output = []

    for doc, emb in zip(documents, embeddings_list):
        output.append({
            "source_id": doc["source_id"],
            "source_type": doc["source_type"],
            "title": doc["title"],
            "text": doc["text"],
            "embedding": emb
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    print(f"تم حفظ {output_file} | أبعاد: {len(embeddings_list[0])}")

# ============================================================
# 4) EVALUATION QUESTIONS
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
        "expected": "table_TABLE_1"
    },
    {
        "question": "What antibiotics are recommended for pregnant women aged 12 years and over?",
        "expected": "table_TABLE_2"
    },
    {
        "question": "What antibiotics are recommended for men aged 16 years and over?",
        "expected": "table_TABLE_3"
    },
    {
        "question": "What antibiotics are recommended for children and young people under 16 years?",
        "expected": "table_TABLE_4"
    }
]

questions = [case["question"] for case in test_cases]
expected_ids = [case["expected"] for case in test_cases]

# ============================================================
# 5) EVALUATE EACH MODEL
# ============================================================

results = []

for model_name, embeddings_file in MODELS:

    print(f"\nتقييم {model_name} ...")

    # Load embeddings
    with open(embeddings_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc_embs = np.array([item["embedding"] for item in data])
    source_ids = [item["source_id"] for item in data]

    # Encode all questions at once
    query_model = SentenceTransformer(model_name)
    query_embs = query_model.encode(questions, normalize_embeddings=True)

    # Compute similarities: (num_queries, num_docs)
    scores = query_embs @ doc_embs.T

    # Get top-k indices for each query
    top_k = 5
    top_indices = np.argsort(scores, axis=1)[:, ::-1][:, :top_k]

    gold_ranks = []

    for i, case in enumerate(test_cases):

        retrieved = [source_ids[idx] for idx in top_indices[i]]

        if case["expected"] in retrieved:
            rank = list(retrieved).index(case["expected"]) + 1
            gold_ranks.append(rank)
        else:
            gold_ranks.append(None)

    found = sum(1 for r in gold_ranks if r is not None)
    recall_at_5 = found / len(test_cases)

    mrr = sum(
        1 / r for r in gold_ranks if r is not None
    ) / len(test_cases)

    results.append({
        "model": model_name,
        "recall": recall_at_5,
        "mrr": mrr,
        "file": embeddings_file
    })

    print(f"Recall@5: {recall_at_5:.4f} | MRR: {mrr:.4f}")

# ============================================================
# 6) PRINT COMPARISON TABLE
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
