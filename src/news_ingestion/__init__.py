"""News ingestion module - fetch from free APIs and manage storage."""

from src.news_ingestion.fetcher import NewsFetcher
from src.news_ingestion.storage import NewsStorage

__all__ = ["NewsFetcher", "NewsStorage"]
