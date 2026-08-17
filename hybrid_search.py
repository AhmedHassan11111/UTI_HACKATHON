import chromadb
from sentence_transformers import SentenceTransformer
import re

# ============================================================
# 1) تحميل الـEmbedding Model
# ============================================================

model = SentenceTransformer("all-MiniLM-L6-v2")

# ============================================================
# 2) فتح Chroma
# ============================================================

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(
    name="uti_guideline"
)

# ============================================================
# 3) دالة استخراج الكلمات المهمة من السؤال
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
# 4) Hybrid Search
# ============================================================

def hybrid_search(query, n_results=5):

    # Semantic Search
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

        # الكلمات المهمة الموجودة في العنوان
        title_words = important_words(title)

        # الكلمات المهمة الموجودة في النص
        text_words = important_words(text)

        title_matches = len(query_words & title_words)
        text_matches = len(query_words & text_words)

        # Semantic similarity
        semantic_score = 1 / (1 + distances[i])

        # Hybrid score
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

    # ترتيب النتائج حسب الـHybrid Score
    scored_results.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    return scored_results[:n_results]


# ============================================================
# 5) مجموعة الاختبار
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
# 6) تشغيل الاختبارات
# ============================================================

print("\n=== HYBRID RETRIEVAL EVALUATION ===")

gold_ranks = []

for case in test_cases:

    print("\nQuestion:")
    print(case["question"])

    results = hybrid_search(case["question"])

    print("\nResults:")

    for rank, result in enumerate(results, start=1):

        print(
            rank,
            "->",
            result["id"],
            "| hybrid:",
            round(result["hybrid_score"], 4),
            "| title matches:",
            result["title_matches"]
        )

    result_ids = [x["id"] for x in results]

    if case["expected"] in result_ids:

        rank = result_ids.index(case["expected"]) + 1

        gold_ranks.append(rank)

        print("Gold found at rank:", rank)

    else:

        gold_ranks.append(None)

        print("Gold NOT found in Top 5")


# ============================================================
# 7) حساب Recall@5 و MRR
# ============================================================

found = sum(
    1 for rank in gold_ranks
    if rank is not None
)

recall_at_5 = found / len(test_cases)

mrr = sum(
    1 / rank
    for rank in gold_ranks
    if rank is not None
) / len(test_cases)

print("\n=== EVALUATION SUMMARY ===")

print("Total test cases:", len(test_cases))

print("Gold documents found:", found)

print(
    "Recall@5:",
    round(recall_at_5, 4)
)

print(
    "MRR:",
    round(mrr, 4)
)