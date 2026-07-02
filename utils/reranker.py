from sentence_transformers import CrossEncoder
from functools import lru_cache


@lru_cache(maxsize=1)
def load_reranker():

    print("Loading CrossEncoder...")

    return CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )


class Reranker:

    def __init__(self):

        self.model = load_reranker()

    def rerank(
        self,
        question,
        documents,
        sources,
        top_k=5
    ):

        if not documents:
            return [], []

        pairs = [
            (question, doc)
            for doc in documents
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(documents, sources, scores),
            key=lambda x: x[2],
            reverse=True
        )

        reranked_documents = []
        reranked_sources = []

        for doc, source, _ in ranked[:top_k]:

            reranked_documents.append(doc)
            reranked_sources.append(source)

        return reranked_documents, reranked_sources