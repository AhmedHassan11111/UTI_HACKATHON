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
# 3) استخراج الكلمات المهمة
# ============================================================

def important_words(text):

    text = text.lower()

    words = re.findall(
        r"[a-z]+(?:-[a-z]+)?",
        text
    )

    stop_words = {
        "what", "are", "the", "for", "with",
        "and", "over", "years", "is", "in",
        "recommended", "should", "be", "to",
        "of", "a", "an", "when", "who"
    }

    return set(
        word
        for word in words
        if word not in stop_words
    )


# ============================================================
# 4) Hybrid Retrieval
# ============================================================

def retrieve(query, n_results=3):

    query_embedding = model.encode(
        query
    ).tolist()

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

        title = metadata.get(
            "title",
            ""
        ).lower()

        text = documents[i].lower()

        title_words = important_words(
            title
        )

        text_words = important_words(
            text
        )

        title_matches = len(
            query_words & title_words
        )

        text_matches = len(
            query_words & text_words
        )

        semantic_score = (
            1 / (1 + distances[i])
        )

        hybrid_score = (
            semantic_score
            + (title_matches * 0.30)
            + (text_matches * 0.05)
        )

        scored_results.append({
            "id": ids[i],
            "title": metadata.get("title"),
            "pages": metadata.get("pages"),
            "text": documents[i],
            "score": hybrid_score
        })

    scored_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored_results[:n_results]


# ============================================================
# 5) السؤال التجريبي
# ============================================================

query = (
    "What antibiotics are recommended for "
    "non-pregnant women aged 16 years and over?"
)

# ============================================================
# 6) استرجاع المصادر
# ============================================================

results = retrieve(
    query,
    n_results=3
)


# ============================================================
# 7) بناء الـContext
# ============================================================

context_parts = []

for i, result in enumerate(
    results,
    start=1
):

    context_parts.append(
        f"""
SOURCE {i}
ID: {result["id"]}
TITLE: {result["title"]}
PAGES: {result["pages"]}

TEXT:
{result["text"]}
"""
    )


context = "\n".join(
    context_parts
)


# ============================================================
# 8) عرض الـContext
# ============================================================

print("\n=== QUERY ===")
print(query)

print("\n=== RETRIEVED CONTEXT ===")
print(context)

print("\n=== CONTEXT READY ===")
print("Number of sources:", len(results))