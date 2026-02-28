"""Free News API fetcher - Saurav's NewsAPI (no API key required)."""

import hashlib
import json
from datetime import datetime
from typing import Any, Optional

import httpx

from config.settings import settings


class NewsFetcher:
    """Fetches news from free APIs - Saurav's NewsAPI (https://saurav.tech/NewsAPI/)."""

    BASE_URL = "https://saurav.tech/NewsAPI"
    COUNTRIES = ["in", "us", "gb", "au", "fr"]
    CATEGORIES = ["technology", "business", "science", "health", "sports", "entertainment", "general"]

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.news_api_base

    def _generate_id(self, article: dict) -> str:
        """Generate unique ID for article."""
        content = f"{article.get('title', '')}{article.get('url', '')}{article.get('publishedAt', '')}"
        return hashlib.sha256(content.encode()).hexdigest()[:24]

    def _normalize_article(self, article: dict, category: str, country: str) -> dict:
        """Normalize article structure for storage."""
        return {
            "id": self._generate_id(article),
            "title": article.get("title") or "",
            "description": article.get("description") or "",
            "content": article.get("content") or article.get("description") or "",
            "url": article.get("url") or "",
            "source": article.get("source", {}).get("name", "unknown"),
            "author": article.get("author") or "Unknown",
            "published_at": article.get("publishedAt", ""),
            "category": category,
            "country": country,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }

    async def fetch_top_headlines(
        self,
        category: Optional[str] = None,
        country: str = "us",
    ) -> list[dict]:
        """Fetch top headlines. No API key required."""
        category = category or "general"
        url = f"{self.base_url}/top-headlines/category/{category}/{country}.json"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        articles = data.get("articles", [])
        return [
            self._normalize_article(a, category, country)
            for a in articles
            if a.get("title") and a.get("title") != "[Removed]"
        ]

    async def fetch_everything(self, source_id: str = "bbc-news") -> list[dict]:
        """Fetch everything from a source (bbc-news, cnn, fox-news, google-news)."""
        url = f"{self.base_url}/everything/{source_id}.json"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        articles = data.get("articles", [])
        return [
            self._normalize_article(a, "general", "gb")
            for a in articles
            if a.get("title") and a.get("title") != "[Removed]"
        ]

    async def fetch_all(self) -> list[dict]:
        """Fetch news from all categories and countries (comprehensive ingestion)."""
        all_articles: list[dict] = []
        seen_ids: set[str] = set()

        for country in self.COUNTRIES:
            for category in self.CATEGORIES:
                try:
                    articles = await self.fetch_top_headlines(category=category, country=country)
                    for a in articles:
                        if a["id"] not in seen_ids:
                            seen_ids.add(a["id"])
                            all_articles.append(a)
                except Exception:
                    continue

        return all_articles
