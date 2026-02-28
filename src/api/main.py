"""FastAPI application for News Intelligence System."""

from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.workflows import NewsIntelligenceAgent
from src.news_ingestion.fetcher import NewsFetcher
from src.news_ingestion.storage import NewsStorage
from src.vector_db.endee_client import EndeeVectorStore

app = FastAPI(
    title="News Intelligence System",
    description="AI-powered news with semantic search, RAG, and recommendations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = NewsIntelligenceAgent()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    category: Optional[str] = None
    country: Optional[str] = None


class AskRequest(BaseModel):
    query: str
    top_k: int = 5


class RecommendRequest(BaseModel):
    interests: list[str]
    top_k: int = 10
    category: Optional[str] = None


@app.get("/")
def root():
    return {"message": "News Intelligence System API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search")
def semantic_search(req: SearchRequest):
    """Semantic search over news using Endee."""
    results = agent.vector_store.semantic_search(
        query=req.query,
        top_k=req.top_k,
        category=req.category,
        country=req.country,
    )
    return {"query": req.query, "results": results}


@app.post("/ask")
def rag_ask(req: AskRequest):
    """RAG: ask questions answered from news context."""
    return agent.rag.ask(req.query, top_k=req.top_k)


@app.post("/recommend")
def recommend(req: RecommendRequest):
    """Get personalized news recommendations."""
    recs = agent.recommender.recommend(
        user_interests=req.interests,
        top_k=req.top_k,
        category=req.category,
    )
    return {"recommendations": recs}


@app.post("/workflow")
def run_workflow(
    task: str = Query(..., description="search, ask, recommend, summarize"),
    query: Optional[str] = None,
):
    """Agentic workflow - route to appropriate handler."""
    return agent.run_workflow(task=task, query=query)


@app.post("/ingest")
async def ingest_news():
    """Fetch news from free API, store, and index in Endee."""
    fetcher = NewsFetcher()
    storage = NewsStorage()
    vector_store = EndeeVectorStore()

    articles = await fetcher.fetch_all()
    storage.save_articles(articles)
    deleted = storage.run_auto_deletion()
    indexed = vector_store.upsert_articles(articles)

    return {
        "fetched": len(articles),
        "indexed": indexed,
        "deleted_old_buckets": deleted,
    }
