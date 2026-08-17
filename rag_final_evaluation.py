import os
os.environ["HF_HOME"] = "D:\\huggingface"

import json
import chromadb
from sentence_transformers import SentenceTransformer
import re

# ============================================================
# 1) CONFIG
# ============================================================

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_PATH = "./chroma_db_final"
COLLECTION_NAME = "uti_guideline_final"
TOP_K = 5

print("=" * 60)
print("RAG FINAL EVALUATION")
print(f"Embedding Model: {EMBEDDING_MODEL}")
print(f"Top-K: {TOP_K}")
print("=" * 60)

# ============================================================
# 2) LOAD DOCUMENTS
# ============================================================

with open("documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

print(f"\nLoaded {len(documents)} documents from documents.json")

# ============================================================
# 3) LOAD EMBEDDING MODEL
# ============================================================

print(f"\nLoading embedding model: {EMBEDDING_MODEL} ...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("Model loaded")

# ============================================================
# 4) CREATE EMBEDDINGS
# ============================================================

texts = [doc["text"] for doc in documents]

print("\nGenerating embeddings ...")
embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
print(f"Generated {len(embeddings)} embeddings | Dimension: {len(embeddings[0])}")

# ============================================================
# 5) BUILD CHROMA DB
# ============================================================

print(f"\nBuilding ChromaDB at {CHROMA_PATH} ...")

client = chromadb.PersistentClient(path=CHROMA_PATH)

# Drop collection if exists
try:
    client.delete_collection(COLLECTION_NAME)
except:
    pass

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

ids = []
docs = []
metas = []
embs = []

for doc, emb in zip(documents, embeddings):
    ids.append(f"{doc['source_type']}_{doc['source_id']}")
    docs.append(doc["text"])
    metas.append({
        "source_type": doc["source_type"],
        "source_id": doc["source_id"],
        "title": doc["title"],
        "pages": ",".join(map(str, doc["pages"]))
    })
    embs.append(emb.tolist())

collection.add(
    ids=ids,
    documents=docs,
    metadatas=metas,
    embeddings=embs
)

print(f"Collection ready with {collection.count()} documents")

# ============================================================
# 6) HELPER: IMPORTANT WORDS
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
# 7) HYBRID SEARCH
# ============================================================

def hybrid_search(query, n_results=TOP_K):
    query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=collection.count()
    )

    result_ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    documents_text = results["documents"][0]

    query_words = important_words(query)

    scored_results = []

    for i in range(len(result_ids)):
        metadata = metadatas[i]
        title = metadata.get("title", "").lower()
        text = documents_text[i].lower()

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
            "id": result_ids[i],
            "title": metadata.get("title"),
            "source_type": metadata.get("source_type"),
            "source_id": metadata.get("source_id"),
            "pages": metadata.get("pages"),
            "distance": distances[i],
            "title_matches": title_matches,
            "text_matches": text_matches,
            "hybrid_score": hybrid_score
        })

    scored_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return scored_results[:n_results]

# ============================================================
# 8) EVALUATION QUESTIONS
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
# 9) RUN EVALUATION
# ============================================================

gold_ranks = []
all_results = []

for idx, case in enumerate(test_cases, 1):
    question = case["question"]
    expected = case["expected"]

    results = hybrid_search(question, n_results=TOP_K)
    result_ids = [x["id"] for x in results]

    found = expected in result_ids
    rank = result_ids.index(expected) + 1 if found else None

    if found:
        gold_ranks.append(rank)
    else:
        gold_ranks.append(None)

    all_results.append({
        "question_num": idx,
        "question": question,
        "expected": expected,
        "results": results,
        "found": found,
        "rank": rank
    })

# ============================================================
# 10) PRINT DETAILED RESULTS
# ============================================================

for res in all_results:
    print("\n" + "=" * 60)
    print(f"Question {res['question_num']}:")
    print(res["question"])
    print("\nRetrieved Results:")

    for i, r in enumerate(res["results"], 1):
        print(f"{i}. ID: {r['id']}")
        print(f"   Score: {r['hybrid_score']:.4f}")
        print(f"   Page: {r['pages']}")
        print(f"   Title: {r['title']}")

    print(f"\nGold Document: {res['expected']}")
    print(f"Gold Found: {'YES' if res['found'] else 'NO'}")
    if res['found']:
        print(f"Gold Rank: {res['rank']}")

# ============================================================
# 11) CALCULATE METRICS
# ============================================================

found_count = sum(1 for r in gold_ranks if r is not None)
recall_at_5 = found_count / len(test_cases)

mrr = sum(1 / r for r in gold_ranks if r is not None) / len(test_cases)

# Precision@5: fraction of retrieved docs that are relevant
# For this prototype, we treat only the gold doc as relevant.
# Precision@5 = (number of questions where gold is in top-5) / (total questions * 5)
# More standard: average per-query precision = (# relevant in top-5) / 5
# Since we have at most 1 relevant doc per query:
precision_at_5 = found_count / (len(test_cases) * TOP_K)

print("\n" + "=" * 60)
print("FINAL METRICS")
print("=" * 60)
print(f"Recall@5: {recall_at_5:.4f}")
print(f"MRR: {mrr:.4f}")
print(f"Precision@5: {precision_at_5:.4f}")
print("=" * 60)
