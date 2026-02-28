"""Application settings loaded from environment."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """News Intelligence System configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Endee Vector Database
    endee_url: str = "http://localhost:8080/api/v1"
    endee_token: Optional[str] = None

    # Ollama LLM (free, local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # News API - Saurav's free API
    news_api_base: str = "https://saurav.tech/NewsAPI"

    # Storage retention
    retention_weeks: int = 4
    retention_months: int = 3
    auto_delete_enabled: bool = True

    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"

    # Index name for Endee
    news_index_name: str = "news_vectors"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
