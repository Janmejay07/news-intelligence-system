"""Recommendation engine - suggest news based on user interests."""

from typing import Optional

from src.vector_db.endee_client import EndeeVectorStore


class RecommendationEngine:
    """Recommends news articles based on semantic similarity to user interests."""

    def __init__(self, vector_store: Optional[EndeeVectorStore] = None):
        self.vector_store = vector_store or EndeeVectorStore()

    def recommend(
        self,
        user_interests: str | list[str],
        top_k: int = 10,
        category: Optional[str] = None,
        exclude_ids: Optional[list[str]] = None,
    ) -> list[dict]:
        """Recommend articles similar to user interests."""
        if isinstance(user_interests, list):
            query = " ".join(user_interests)
        else:
            query = user_interests

        results = self.vector_store.semantic_search(
            query=query,
            top_k=top_k * 2,  # fetch extra to filter
            category=category,
        )

        exclude = set(exclude_ids or [])
        filtered = [r for r in results if r.get("id") not in exclude][:top_k]
        return filtered
