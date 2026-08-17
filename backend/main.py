from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from .ask import hybrid_search, generate_answer


app = FastAPI(title="Med Trace AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5


class Source(BaseModel):
    title: str
    section: str
    snippet: str
    score: float
    page: str = ""


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    results = hybrid_search(request.question, top_k=request.top_k or 5)

    if not results:
        return ChatResponse(
            answer="I couldn't find any relevant sources in the knowledge base for your question. Please try rephrasing or ask about a different UTI-related topic.",
            sources=[]
        )

    best = results[0]
    metadata = best.get("metadata", {})

    answer = generate_answer(request.question, best)

    sources = []
    for i, result in enumerate(results):
        meta = result.get("metadata", {})
        sources.append(Source(
            title=meta.get("title", "Unknown"),
            section=meta.get("source_id", ""),
            snippet=result.get("document", "")[:300] + ("..." if len(result.get("document", "")) > 300 else ""),
            score=round(result.get("hybrid_score", 0), 4),
            page=meta.get("pages", "")
        ))

    return ChatResponse(answer=answer, sources=sources)


@app.get("/health")
def health():
    return {"status": "ok"}
