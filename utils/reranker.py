from functools import lru_cache
from config import RERANKER_MODEL


@lru_cache(maxsize=1)
def load_cross_encoder(model_name: str):
    """Cached singleton for loading the CrossEncoder model."""
    try:
        from sentence_transformers import CrossEncoder
        print(f"Loading CrossEncoder: {model_name}...")
        return CrossEncoder(model_name)
    except Exception as e:
        print(f"Warning: Could not load CrossEncoder ({e}). Reranking will use passthrough.")
        return None


class Reranker:
    """
    Cross-Encoder Reranker for scoring (query, document) pairs
    and re-ordering retrieved chunks by precise semantic relevance.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or RERANKER_MODEL
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = load_cross_encoder(self.model_name)
        return self._model

    def rerank(
        self,
        question: str,
        documents: list[str],
        sources: list[dict],
        top_k: int = 5
    ) -> tuple[list[str], list[dict], list[float]]:
        """
        Rerank documents and sources.
        Returns: (reranked_docs, reranked_sources, relevance_scores)
        """
        if not documents:
            return [], [], []

        if self.model is None or len(documents) <= 1:
            return documents[:top_k], sources[:top_k], [1.0] * min(len(documents), top_k)

        try:
            pairs = [(question, doc) for doc in documents]
            scores = self.model.predict(pairs)

            ranked = sorted(
                zip(documents, sources, scores),
                key=lambda x: x[2],
                reverse=True
            )

            reranked_docs = []
            reranked_sources = []
            reranked_scores = []

            for doc, source, score in ranked[:top_k]:
                reranked_docs.append(doc)
                # Attach relevance score to source metadata
                source_copy = dict(source)
                source_copy["score"] = float(score)
                reranked_sources.append(source_copy)
                reranked_scores.append(float(score))

            return reranked_docs, reranked_sources, reranked_scores

        except Exception as e:
            print(f"Error during reranking: {e}")
            return documents[:top_k], sources[:top_k], [0.5] * min(len(documents), top_k)