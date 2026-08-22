import os
import requests
from functools import lru_cache
from config import EMBEDDING_MODEL, EMBEDDING_PROVIDER, GEMINI_API_KEY


@lru_cache(maxsize=1)
def load_embedding_model(model_name: str):
    """Singleton cached loader for the local sentence transformer embedder."""
    from sentence_transformers import SentenceTransformer
    print(f"Loading local SentenceTransformer Embedder: {model_name}...")
    return SentenceTransformer(model_name)


class Embedder:
    """
    Dual-Mode Embedder Engine:
    1. 'local' (Default): Uses SentenceTransformers on local CPU (100% offline, zero-cost).
    2. 'gemini': Uses Google Gemini Embeddings API (text-embedding-004, ultra-low RAM for cloud deployment).
    """

    def __init__(self, model_name: str = None, provider: str = None, **kwargs):
        self.provider = (provider or EMBEDDING_PROVIDER or "local").lower()
        self.model_name = model_name or EMBEDDING_MODEL
        self._local_model = None

    @property
    def model(self):
        """Lazy loader for local SentenceTransformer model."""
        if self._local_model is None:
            self._local_model = load_embedding_model(self.model_name)
        return self._local_model

    def embed(self, text: str) -> list[float]:
        """Embed a single text string."""
        results = self.embed_batch([text])
        return results[0] if results else []

    def embed_batch(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        """Embed a batch of text strings efficiently."""
        if not texts:
            return []

        # Mode 1: Google Gemini Embeddings API (Cloud deployment / Low RAM mode)
        if self.provider == "gemini":
            return self._embed_gemini(texts)

        # Mode 2: Local SentenceTransformer (Localhost / Offline mode)
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).tolist()

        return embeddings

    def _embed_gemini(self, texts: list[str]) -> list[list[float]]:
        """Call Gemini REST API for text-embedding-004 embeddings."""
        api_key = (os.getenv("GEMINI_API_KEY", "") or GEMINI_API_KEY).strip()
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please add GEMINI_API_KEY to your environment or .env file."
            )

        model_name = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"

        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:batchEmbedContents?key={api_key}"

        embeddings = []
        # Gemini batchEmbedContents accepts up to 100 requests per call
        chunk_size = 64
        for i in range(0, len(texts), chunk_size):
            batch = texts[i : i + chunk_size]
            requests_payload = [
                {
                    "model": model_name,
                    "content": {"parts": [{"text": t}]},
                }
                for t in batch
            ]
            response = requests.post(
                url,
                json={"requests": requests_payload},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Gemini Embedding API error ({response.status_code}): {response.text}"
                )

            data = response.json()
            for emb in data.get("embeddings", []):
                embeddings.append(emb.get("values", []))

        return embeddings