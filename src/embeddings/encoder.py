"""Embedding encoder using sentence-transformers (free, local)."""

from typing import Optional

from config.settings import settings


class EmbeddingEncoder:
    """Encodes text to vectors using sentence-transformers."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None

    @property
    def model(self):
        """Lazy load model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def dimension(self) -> int:
        """Vector dimension from model."""
        return self.model.get_sentence_embedding_dimension()

    def encode(self, texts: str | list[str]) -> list[list[float]]:
        """Encode text(s) to vectors."""
        if isinstance(texts, str):
            texts = [texts]
        vectors = self.model.encode(texts, convert_to_numpy=True)
        return vectors.tolist()
