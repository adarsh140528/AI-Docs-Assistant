from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(self):
        self.documents = []
        self.metadatas = []
        self.bm25 = None

    def build(self, chunks):

        self.documents = chunks

        corpus = [
            chunk["text"].lower().split()
            for chunk in chunks
        ]

        self.metadatas = [
            {"page": chunk["page"]}
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(corpus)

    def search(self, query, k=5):

        if self.bm25 is None:
            return [], []

        tokens = query.lower().split()

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:k]

        documents = []
        metadata = []

        for idx, _ in ranked:

            documents.append(
                self.documents[idx]["text"]
            )

            metadata.append(
                self.metadatas[idx]
            )

        return documents, metadata