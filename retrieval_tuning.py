import chromadb
from sentence_transformers import SentenceTransformer
import re

# ============================================================
# 1) LOAD EMBEDDING MODEL
# ============================================================

model = SentenceTransformer("all-MiniLM-L6-v2")

# ============================================================
# 2) OPEN CHROMA
# ============================================================

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(
    name="uti_guideline"
)

# ============================================================
# 3) HELPER: IMPORTANT WORDS
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

    return set(
        word for word in words
        if word not in stop_words
    )

# ============================================================
# 4) HYBRID SEARCH
# ============================================================

def hybrid_search(query, n_results=5):

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10
    )

    ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]

    query_words = important_words(query)

    scored_results = []

    for i in range(len(ids)):

        metadata = metadatas[i]

        title = metadata.get("title", "").lower()
        text = documents[i].lower()

        title_words = important_words(title)
        text_words = important_words(text)

        title_matches = len(query_words & title_words)
        text_matches = len(query_words & text_words)

        semantic_score = 1 / (1 + distances[i])

        hybrid_score = (
            semantic_score
            + (title_matches * 0.30)
            + (text_matches * 0.05)
        )

        scored_results.append({
            "id": ids[i],
            "title": metadata.get("title"),
            "distance": distances[i],
            "title_matches": title_matches,
            "text_matches": text_matches,
            "hybrid_score": hybrid_score
        })

    scored_results.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    return scored_results[:n_results]

# ============================================================
# 5) EVALUATION CASES
# ============================================================

test_cases = [
    {
        "question": "What is a lower urinary tract infection?",
        "expected": "recommendation_1.1.1"
    },
    {
        "question": "What advice should be given to all people with lower UTI about managing symptoms?",
        "expected": "recommendation_1.1.2"
    },
    {
        "question": "What should be done if symptoms do not start to improve within 48 hours or worsen at any time for women with lower UTI who are not pregnant?",
        "expected": "recommendation_1.1.3"
    },
    {
        "question": "What should be done when microbiological results are available after a urine sample was sent for culture and susceptibility testing?",
        "expected": "recommendation_1.1.4"
    },
    {
        "question": "What should be done for pregnant women and men with lower UTI?",
        "expected": "recommendation_1.1.5"
    },
    {
        "question": "What should people with lower UTI be advised to use for pain?",
        "expected": "recommendation_1.3.1"
    },
    {
        "question": "What should be considered when prescribing antibiotics for lower UTI?",
        "expected": "recommendation_1.4.1"
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

# ============================================================
# 6) EVALUATION RUNNER
# ============================================================

def evaluate_for_k(k, show_details=False):

    gold_ranks = []
    details = []

    for case in test_cases:

        question = case["question"]
        expected = case["expected"]

        results = hybrid_search(question, n_results=k)

        result_ids = [x["id"] for x in results]

        if expected in result_ids:

            rank = result_ids.index(expected) + 1
            gold_ranks.append(rank)

        else:

            gold_ranks.append(None)

        if show_details:

            details.append({
                "question": question,
                "expected": expected,
                "retrieved": result_ids,
                "found": expected in result_ids,
                "rank": rank if expected in result_ids else None
            })

    found = sum(
        1 for rank in gold_ranks
        if rank is not None
    )

    recall_at_k = found / len(test_cases)

    mrr = sum(
        1 / rank
        for rank in gold_ranks
        if rank is not None
    ) / len(test_cases)

    return {
        "k": k,
        "recall": recall_at_k,
        "mrr": mrr,
        "found": found,
        "total": len(test_cases),
        "gold_ranks": gold_ranks,
        "details": details
    }

# ============================================================
# 7) MAIN
# ============================================================

if __name__ == "__main__":

    k_values = [1, 3, 5, 7]

    results = {}

    for k in k_values:

        res = evaluate_for_k(k, show_details=True)
        results[k] = res

    # ========================================================
    # PRINT TABLE
    # ========================================================

    print("\nTop-K Retrieval Evaluation")
    print("-" * 50)
    print(f"{'K':<6} {'Recall@K':<12} {'MRR':<12}")
    print("-" * 50)

    for k in k_values:

        res = results[k]

        print(
            f"{k:<6} "
            f"{res['recall']:<12.4f} "
            f"{res['mrr']:<12.4f}"
        )

    print("-" * 50)

    # ========================================================
    # PER-QUESTION DETAILS
    # ========================================================

    print("\nPer-Question Retrieval Details")
    print("=" * 60)

    for case in test_cases:

        print("\nQuestion:")
        print(case["question"])
        print("Gold:", case["expected"])

        for k in k_values:

            res = results[k]
            detail = res["details"][test_cases.index(case)]

            print(f"\nK={k}")
            print("Retrieved:")

            for rank, rid in enumerate(detail["retrieved"], start=1):

                marker = " *" if rid == case["expected"] else ""
                print(f"  {rank}. {rid}{marker}")

            if detail["found"]:

                print(f"Gold found at rank: {detail['rank']}")

            else:

                print("Gold NOT found")

    # ========================================================
    # ANALYSIS
    # ========================================================

    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    best_recall_k = max(k_values, key=lambda k: results[k]["recall"])
    best_mrr_k = max(k_values, key=lambda k: results[k]["mrr"])

    print(f"Best Recall@K: K={best_recall_k} (Recall={results[best_recall_k]['recall']:.4f})")
    print(f"Best MRR:      K={best_mrr_k} (MRR={results[best_mrr_k]['mrr']:.4f})")

    recall_values = [results[k]["recall"] for k in k_values]
    mrr_values = [results[k]["mrr"] for k in k_values]

    recall_improving = all(
        recall_values[i] <= recall_values[i + 1]
        for i in range(len(recall_values) - 1)
    )

    mrr_improving = all(
        mrr_values[i] <= mrr_values[i + 1]
        for i in range(len(mrr_values) - 1)
    )

    print(f"\nRecall increases with K: {'Yes' if recall_improving else 'No'}")
    print(f"MRR increases with K:    {'Yes' if mrr_improving else 'No'}")

    recommended_k = best_recall_k

    if results[best_recall_k]["recall"] == 1.0:

        recommended_k = min(
            k for k in k_values
            if results[k]["recall"] == 1.0
        )

    print(f"\nRecommended Top-K: {recommended_k}")
    print(f"Reason: Achieves Recall@K = {results[recommended_k]['recall']:.4f} "
          f"with MRR = {results[recommended_k]['mrr']:.4f}. "
          f"Higher K does not improve recall beyond this point.")

    # ========================================================
    # COMPARISON WITH PREVIOUS RESULTS
    # ========================================================

    print("\n" + "=" * 60)
    print("COMPARISON WITH PREVIOUS RESULTS")
    print("=" * 60)
    print("Previous: Recall@5 = 1.0, MRR = 0.8409")
    print(f"Current K=5: Recall@5 = {results[5]['recall']:.4f}, MRR = {results[5]['mrr']:.4f}")

    if results[5]["recall"] == 1.0 and abs(results[5]["mrr"] - 0.8409) < 0.001:

        print("Results match previous evaluation.")

    else:

        print("Results differ from previous evaluation.")
