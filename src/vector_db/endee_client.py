"""Endee vector database client for semantic search.

Uses Endee (https://github.com/endee-io/endee) - high-performance vector DB.
Fork and use: https://github.com/Janmejay07/endee
"""

from typing import Any, Optional

from config.settings import settings


class EndeeVectorStore:
    """Endee-backed vector store for news articles."""

    def __init__(
        self,
        index_name: Optional[str] = None,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.index_name = index_name or settings.news_index_name
        self._client = None
        self._index = None
        self._base_url = base_url or settings.endee_url
        self._token = token or settings.endee_token
        self._encoder = None

    def _get_client(self):
        """Lazy init Endee client."""
        if self._client is None:
            from endee import Endee
            kwargs = {}
            if self._token:
                kwargs["token"] = self._token
            self._client = Endee(**kwargs)
            self._client.set_base_url(self._base_url)
        return self._client

    def _get_encoder(self):
        """Lazy init encoder."""
        if self._encoder is None:
            from src.embeddings.encoder import EmbeddingEncoder
            self._encoder = EmbeddingEncoder()
        return self._encoder

    def ensure_index(self, dimension: int = 384) -> None:
        """Create index if not exists. Dimension matches all-MiniLM-L6-v2."""
        client = self._get_client()
        indexes = client.list_indexes()
        index_names = [i.get("name", i) if isinstance(i, dict) else str(i) for i in (indexes or [])]
        if self.index_name not in index_names:
            try:
                from endee import Precision
                client.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    space_type="cosine",
                    precision=Precision.FLOAT16,  # Compatible with both SDK and API
                )
            except Exception as e:
                from endee.exceptions import ConflictException
                if not isinstance(e, ConflictException):
                    raise
        self._index = client.get_index(name=self.index_name)

    def upsert_articles(self, articles: list[dict]) -> int:
        """Upsert articles with embeddings into Endee."""
        encoder = self._get_encoder()
        self.ensure_index(dimension=encoder.dimension)

        vectors_to_upsert = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}".strip()
            if not text:
                continue
            vector = encoder.encode(text)[0]
            meta = {
                "title": article.get("title", ""),
                "description": article.get("description", "")[:500],
                "url": article.get("url", ""),
                "source": article.get("source", ""),
                "category": article.get("category", ""),
                "country": article.get("country", ""),
                "published_at": article.get("published_at", ""),
            }
            vectors_to_upsert.append({
                "id": article["id"],
                "vector": vector,
                "meta": meta,
                "filter": {"category": meta["category"], "country": meta["country"]},
            })

        batch_size = 1000  # Endee limit per upsert
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i : i + batch_size]
            self._index.upsert(batch)
        return len(vectors_to_upsert)

    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        category: Optional[str] = None,
        country: Optional[str] = None,
    ) -> list[dict]:
        """Semantic search over news using Endee."""
        encoder = self._get_encoder()
        self.ensure_index(dimension=encoder.dimension)

        query_vector = encoder.encode(query)[0]
        filters = []
        if category:
            filters.append({"category": {"$eq": category}})
        if country:
            filters.append({"country": {"$eq": country}})

        results = self._index.query(
            vector=query_vector,
            top_k=top_k,
            filter=filters if filters else None,
        )
        return [{"id": r["id"], "similarity": r.get("similarity", 0), "meta": r.get("meta", {})} for r in results]
