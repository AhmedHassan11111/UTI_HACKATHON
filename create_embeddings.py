import json
from sentence_transformers import SentenceTransformer

# ============================================================
# 1) قراءة الـDataset
# ============================================================

with open("documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

print("عدد الـDocuments:", len(documents))

# ============================================================
# 2) تحميل الـEmbedding Model
# ============================================================

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded")

# ============================================================
# 3) استخراج النصوص
# ============================================================

texts = [
    document["text"]
    for document in documents
]

# ============================================================
# 4) تحويل النصوص إلى Embeddings
# ============================================================

embeddings = model.encode(
    texts,
    show_progress_bar=True
)

print("تم إنشاء الـEmbeddings")
print("عدد الـEmbeddings:", len(embeddings))
print("أبعاد كل Embedding:", len(embeddings[0]))

# ============================================================
# 5) إضافة الـEmbedding لكل Document
# ============================================================

for document, embedding in zip(documents, embeddings):
    document["embedding"] = embedding.tolist()

# ============================================================
# 6) حفظ النتيجة
# ============================================================

with open("documents_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(
        documents,
        f,
        ensure_ascii=False,
        indent=2
    )

print("تم إنشاء documents_embeddings.json")