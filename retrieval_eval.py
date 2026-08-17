import chromadb
from sentence_transformers import SentenceTransformer

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
# 3) أسئلة الاختبار
# ============================================================

test_cases = [
    {
        "question": "What antibiotics are recommended for non-pregnant women aged 16 years and over?",
        "expected_id": "table_TABLE_1"
    },
    {
        "question": "What antibiotics are recommended for pregnant women aged 12 years and over?",
        "expected_id": "table_TABLE_2"
    },
    {
        "question": "What antibiotics are recommended for men aged 16 years and over?",
        "expected_id": "table_TABLE_3"
    }
]

# ============================================================
# 4) تشغيل الاختبارات
# ============================================================

print("\n=== RETRIEVAL EVALUATION ===")

for case in test_cases:

    question = case["question"]
    expected_id = case["expected_id"]

    query_embedding = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    result_ids = results["ids"][0]

    print("\nQuestion:")
    print(question)

    print("Expected:")
    print(expected_id)

    print("Retrieved:")

    for rank, result_id in enumerate(result_ids, start=1):
        print(
            rank,
            "->",
            result_id,
            "| distance:",
            results["distances"][0][rank - 1]
        )

    # هل الـGold Document ظهر في أول 5؟
    if expected_id in result_ids:

        rank = result_ids.index(expected_id) + 1

        print("Gold found at rank:", rank)

    else:

        print("Gold NOT found in Top 5")