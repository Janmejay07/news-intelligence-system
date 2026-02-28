"""Agentic AI workflows - multi-step reasoning over news."""

from typing import Optional

from src.rag.pipeline import RAGPipeline
from src.recommendations.engine import RecommendationEngine
from src.vector_db.endee_client import EndeeVectorStore


class NewsIntelligenceAgent:
    """Agent that orchestrates search, RAG, and recommendations."""

    def __init__(self):
        self.vector_store = EndeeVectorStore()
        self.rag = RAGPipeline(vector_store=self.vector_store)
        self.recommender = RecommendationEngine(vector_store=self.vector_store)

    def run_workflow(
        self,
        task: str,
        query: Optional[str] = None,
        user_interests: Optional[list[str]] = None,
    ) -> dict:
        """
        Agentic workflow: route task to appropriate handler.
        Tasks: search, ask, recommend, summarize
        """
        task_lower = task.strip().lower()

        if task_lower == "search" and query:
            results = self.vector_store.semantic_search(query, top_k=10)
            return {"task": "search", "results": results}

        if task_lower == "ask" and query:
            return {"task": "ask", **self.rag.ask(query, top_k=5)}

        if task_lower == "recommend":
            interests = user_interests or [query or "technology"]
            recs = self.recommender.recommend(interests, top_k=10)
            return {"task": "recommend", "recommendations": recs}

        if task_lower == "summarize" and query:
            answer = self.rag.ask(
                f"Summarize the main points and key takeaways from news about: {query}",
                top_k=8,
            )
            return {"task": "summarize", **answer}

        return {"task": task, "error": "Unknown task or missing query. Use: search, ask, recommend, summarize."}
