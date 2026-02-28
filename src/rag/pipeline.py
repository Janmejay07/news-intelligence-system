"""RAG pipeline - retrieve relevant news and generate LLM answers."""

from typing import Optional

from config.settings import settings


class RAGPipeline:
    """Retrieval Augmented Generation using Endee + Ollama."""

    def __init__(
        self,
        vector_store=None,
        model: Optional[str] = None,
    ):
        from src.vector_db.endee_client import EndeeVectorStore
        self.vector_store = vector_store or EndeeVectorStore()
        self.model = model or settings.ollama_model
        self.ollama_url = settings.ollama_base_url

    def _retrieve(self, query: str, top_k: int = 5, **filters) -> list[dict]:
        """Retrieve relevant news from Endee."""
        return self.vector_store.semantic_search(query, top_k=top_k, **filters)

    def _build_context(self, results: list[dict]) -> str:
        """Build context string from retrieved articles."""
        context_parts = []
        for r in results:
            meta = r.get("meta", r)
            title = meta.get("title", "")
            desc = meta.get("description", "")
            content = desc or str(meta)[:500]
            context_parts.append(f"- {title}\n  {content}")
        return "\n\n".join(context_parts) if context_parts else "No relevant articles found."

    def _generate(self, query: str, context: str) -> str:
        """Generate answer using Ollama (free local LLM)."""
        import httpx

        prompt = f"""Based on the following news articles, answer the question. If the articles don't contain relevant information, say so.

News context:
{context}

Question: {query}

Answer:"""

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
                return response.json().get("response", "Unable to generate response.")
        except Exception as e:
            return f"LLM error (ensure Ollama is running with model {self.model}): {e}"

    def ask(self, query: str, top_k: int = 5, **filters) -> dict:
        """RAG: retrieve + generate answer."""
        results = self._retrieve(query, top_k=top_k, **filters)
        context = self._build_context(results)
        answer = self._generate(query, context)
        return {
            "query": query,
            "answer": answer,
            "sources": [r.get("meta", r) for r in results],
            "context_preview": context[:500] + "..." if len(context) > 500 else context,
        }
