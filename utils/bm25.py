import re
from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric words."""
    if not text:
        return []
    return re.findall(r"\b\w+\b", text.lower())


class BM25Retriever:
    """
    BM25 Sparse Lexical Retriever for exact keyword and terminology matching.
    """

    def __init__(self):
        self.documents = []
        self.metadatas = []
        self.bm25 = None

    def build(self, chunks: list[dict]):
        """Build BM25 index from a list of chunk dictionaries."""
        self.documents = [chunk["text"] for chunk in chunks]
        self.metadatas = [
            {
                "page": chunk.get("page", 1),
                "source": chunk.get("source", "Document"),
                "chunk_index": chunk.get("chunk_index", i)
            }
            for i, chunk in enumerate(chunks)
        ]

        corpus = [tokenize(doc) for doc in self.documents]
        # Avoid empty token lists for BM25Okapi
        cleaned_corpus = [tokens if tokens else ["empty"] for tokens in corpus]
        self.bm25 = BM25Okapi(cleaned_corpus)

    def search(self, query: str, k: int = 5) -> tuple[list[str], list[dict]]:
        """
        Search for top-k BM25 matches.
        Returns: (documents, metadatas)
        """
        if self.bm25 is None or not self.documents:
            return [], []

        tokens = tokenize(query)
        if not tokens:
            return [], []

        scores = self.bm25.get_scores(tokens)

        # Pair indices with scores and filter positive scores
        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:k]

        docs = []
        metas = []

        for idx, score in ranked:
            if score > 0:  # Only return documents with matching keywords
                docs.append(self.documents[idx])
                metas.append(self.metadatas[idx])

        return docs, metas