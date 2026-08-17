import json

# ============================================================
# 1) قراءة Recommendations
# ============================================================

with open("recommendation_chunks.json", "r", encoding="utf-8") as f:
    recommendations = json.load(f)

# ============================================================
# 2) قراءة Tables
# ============================================================

with open("table_chunks.json", "r", encoding="utf-8") as f:
    tables = json.load(f)

# ============================================================
# 3) تجهيز Dataset موحّد
# ============================================================

documents = []

for item in recommendations:
    documents.append({
        "source_type": "recommendation",
        "source_id": item["recommendation_id"],
        "title": item["recommendation_id"],
        "pages": item["pages"],
        "text": item["text"]
    })

for item in tables:
    documents.append({
        "source_type": "table",
        "source_id": item["table_id"],
        "title": item["title"],
        "pages": item["pages"],
        "text": item["text"]
    })

# ============================================================
# 4) حفظ الـDataset
# ============================================================

with open("documents.json", "w", encoding="utf-8") as f:
    json.dump(
        documents,
        f,
        ensure_ascii=False,
        indent=2
    )

print("تم إنشاء documents.json")
print("عدد الـDocuments:", len(documents))
print("Recommendations:", len(recommendations))
print("Tables:", len(tables))