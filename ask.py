import chromadb
from sentence_transformers import SentenceTransformer
import re


# ============================================================
# 1) LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded")


# ============================================================
# 2) LOAD CHROMA DATABASE
# ============================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="uti_guideline"
)

print("Vector database loaded")
print("Documents:", collection.count())


# ============================================================
# 3) TITLE / KEYWORD MATCHING
# ============================================================

def title_matches(query, metadata):

    title = metadata.get("title", "").lower()

    query_lower = query.lower()

    query_words = re.findall(
        r"[a-zA-Z]+",
        query_lower
    )

    matches = 0

    # General word matching
    for word in query_words:

        if len(word) < 3:
            continue

        if word in title:
            matches += 1

    # Important clinical table matching
    if "non-pregnant" in query_lower and "non-pregnant" in title:
        matches += 3

    if "pregnant" in query_lower and "pregnant" in title:
        matches += 3

    if "men" in query_lower and "men" in title:
        matches += 3

    if "children" in query_lower and "children" in title:
        matches += 3

    if "under 16" in query_lower and "under 16" in title:
        matches += 2

    if "16 years and over" in query_lower and "16 years and over" in title:
        matches += 2

    return matches


# ============================================================
# 4) HYBRID SEARCH
# ============================================================

def hybrid_search(query, top_k=5):

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )[0].tolist()

    # Search all documents
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=collection.count()
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    candidates = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        matches = title_matches(
            query,
            metadata
        )

        # Semantic similarity
        semantic_score = 1 - distance

        # Hybrid score
        hybrid_score = (
            semantic_score
            + (matches * 0.25)
        )

        candidates.append({
            "document": document,
            "metadata": metadata,
            "distance": distance,
            "matches": matches,
            "hybrid_score": hybrid_score
        })

    # Highest score first
    candidates.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    return candidates[:top_k]


# ============================================================
# 5) GENERATE SOURCE-BASED ANSWER
# ============================================================

def generate_answer(query, best):

    metadata = best["metadata"]
    text = best["document"]

    source_type = metadata.get(
        "source_type",
        ""
    )

    source_id = metadata.get(
        "source_id",
        ""
    )

    title = metadata.get(
        "title",
        ""
    )

    pages = metadata.get(
        "pages",
        ""
    )

    # --------------------------------------------------------
    # Table-based answer
    # --------------------------------------------------------

    if source_type == "table":

        # Non-pregnant women
        if source_id == "TABLE_1":

            return f"""
According to {title}:

First choices:
- Nitrofurantoin
- Trimethoprim

Second choices, if the first choice is not suitable or
there is no improvement after at least 48 hours:
- Nitrofurantoin
- Pivmecillinam
- Fosfomycin

The exact dosage and duration are given in the source table.
"""

        # Pregnant women
        if source_id == "TABLE_2":

            return f"""
According to {title}:

First choice:
- Nitrofurantoin

Second choices:
- Amoxicillin, only if culture results are available and susceptible
- Cefalexin

The table also gives antibiotic choices for asymptomatic
bacteriuria based on recent culture and susceptibility results.
"""

        # Men
        if source_id == "TABLE_3":

            return f"""
According to {title}:

First choices:
- Trimethoprim
- Nitrofurantoin, when eGFR is 45 ml/minute or more

The source specifically states that nitrofurantoin is not
recommended for men with suspected prostate involvement.
"""

        # Children
        if source_id == "TABLE_4":

            return f"""
According to {title}:

For children aged 3 months and over, first choices include:
- Trimethoprim, when there is a low risk of resistance
- Nitrofurantoin, when eGFR is 45 ml/minute or more

Second choices include:
- Nitrofurantoin
- Amoxicillin, when culture results are available and susceptible
- Cefalexin

Children under 3 months should be referred to a paediatric
specialist according to the source.
"""

    # --------------------------------------------------------
    # Recommendation-based answer
    # --------------------------------------------------------

    return f"""
According to recommendation {source_id}:

{text}
"""


# ============================================================
# 6) PRINT ANSWER
# ============================================================

def answer_question(query):

    results = hybrid_search(
        query,
        top_k=5
    )

    if not results:
        print("No evidence found.")
        return

    best = results[0]

    metadata = best["metadata"]

    # ========================================================
    # QUESTION
    # ========================================================

    print("\n" + "=" * 60)
    print("QUESTION")
    print("=" * 60)

    print(query)

    # ========================================================
    # ANSWER
    # ========================================================

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)

    answer = generate_answer(
        query,
        best
    )

    print(answer)

    # ========================================================
    # SOURCE
    # ========================================================

    print("=" * 60)
    print("SOURCE")
    print("=" * 60)

    print(
        "Source ID:",
        metadata.get("source_id")
    )

    print(
        "Source type:",
        metadata.get("source_type")
    )

    print(
        "Title:",
        metadata.get("title")
    )

    print(
        "Page(s):",
        metadata.get("pages")
    )

    print(
        "Hybrid score:",
        round(best["hybrid_score"], 4)
    )

    # ========================================================
    # EVIDENCE
    # ========================================================

    print("\n" + "=" * 60)
    print("EVIDENCE")
    print("=" * 60)

    print(best["document"])

    # ========================================================
    # RETRIEVAL RESULTS
    # ========================================================

    print("\n" + "=" * 60)
    print("OTHER RETRIEVED SOURCES")
    print("=" * 60)

    for i, result in enumerate(results[1:], start=2):

        meta = result["metadata"]

        print(
            f"{i}.",
            meta.get("source_id"),
            "|",
            meta.get("source_type"),
            "| score:",
            round(result["hybrid_score"], 4)
        )


# ============================================================
# 7) MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print()
    print("UTI CLINICAL DECISION SUPPORT")
    print("=" * 60)
    print("Hybrid Retrieval + Evidence")
    print("Type 'exit' to quit.")
    print()

    while True:

        question = input("Question: ").strip()

        if question.lower() == "exit":

            print("Goodbye.")
            break

        if not question:
            continue

        answer_question(question)