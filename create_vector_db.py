import json
import chromadb

# ============================================================
# 1) قراءة الـEmbeddings
# ============================================================

with open("documents_embeddings.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

print("عدد الـDocuments:", len(documents))

# ============================================================
# 2) إنشاء Chroma Database محلية
# ============================================================

client = chromadb.PersistentClient(path="./chroma_db")

# ============================================================
# 3) إنشاء Collection
# ============================================================

collection = client.get_or_create_collection(
    name="uti_guideline"
)

print("Collection جاهزة")

# ============================================================
# 4) تجهيز البيانات
# ============================================================

ids = []
embeddings = []
documents_text = []
metadatas = []

for item in documents:

    ids.append(
        f"{item['source_type']}_{item['source_id']}"
    )

    embeddings.append(item["embedding"])

    documents_text.append(item["text"])

    metadatas.append({
        "source_type": item["source_type"],
        "source_id": item["source_id"],
        "title": item["title"],
        "pages": ",".join(map(str, item["pages"]))
    })

# ============================================================
# 5) إدخال البيانات في Chroma
# ============================================================

collection.upsert(
    ids=ids,
    embeddings=embeddings,
    documents=documents_text,
    metadatas=metadatas
)

# ============================================================
# 6) التحقق
# ============================================================

print("تم إدخال البيانات في Chroma")
print("عدد العناصر داخل Collection:", collection.count())
print("Vector Database جاهزة")