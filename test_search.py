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
# 3) السؤال
# ============================================================

query = "Table 1 Antibiotics for non-pregnant women aged 16 years and over"

# ============================================================
# 4) تحويل السؤال إلى Embedding
# ============================================================

query_embedding = model.encode(query).tolist()

# ============================================================
# 5) البحث
# ============================================================

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=4
)

# ============================================================
# 6) عرض النتائج
# ============================================================

print("\n=== RETRIEVAL DIAGNOSTIC ===")

for i in range(len(results["ids"][0])):

    print("\n--- Result", i + 1, "---")
    print("ID:", results["ids"][0][i])
    print("Distance:", results["distances"][0][i])
    print("Title:", results["metadatas"][0][i]["title"])

# ============================================================
# 7) مقارنة مباشرة بين Table 1 و Table 2
# ============================================================

table1 = collection.get(
    ids=["table_TABLE_1"],
    include=["embeddings"]
)

table2 = collection.get(
    ids=["table_TABLE_2"],
    include=["embeddings"]
)

from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

sim1 = cosine_similarity(
    query_embedding,
    table1["embeddings"][0]
)

sim2 = cosine_similarity(
    query_embedding,
    table2["embeddings"][0]
)

print("\n=== DIRECT COMPARISON ===")
print("Similarity with TABLE_1:", sim1)
print("Similarity with TABLE_2:", sim2)