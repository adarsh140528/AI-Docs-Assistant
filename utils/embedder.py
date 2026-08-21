from functools import lru_cache
from config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def load_embedding_model(model_name: str):
    """Singleton cached loader for the local sentence transformer embedder."""
    from sentence_transformers import SentenceTransformer
    print(f"Loading local SentenceTransformer Embedder: {model_name}...")
    return SentenceTransformer(model_name)


class Embedder:
    """
    High-speed, 100% reliable local embedder using SentenceTransformers.
    Zero API rate limits, zero network failures, zero cost.
    """

    def __init__(self, model_name: str = None, **kwargs):
        self.model_name = model_name or EMBEDDING_MODEL
        self._model = None
        self.provider = "local"

    @property
    def model(self):
        if self._model is None:
            self._model = load_embedding_model(self.model_name)
        return self._model

    def embed(self, text: str) -> list[float]:
        """Embed a single text string."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        """Embed a batch of text strings efficiently."""
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).tolist()

        return embeddings