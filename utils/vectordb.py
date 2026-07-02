import chromadb


class VectorDB:

    def __init__(self, db_path):

        self.db_path = db_path

        self.client = chromadb.PersistentClient(
            path=db_path
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_documents(
        self,
        chunks,
        embeddings
    ):

        ids = []

        documents = []

        metadatas = []

        for i, chunk in enumerate(chunks):

            ids.append(f"doc_{i}")

            documents.append(
                chunk["text"]
            )

            metadatas.append({
                "page": chunk["page"]
            })

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding,
        k=5
    ):

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        return results

    def close(self):
        """
        Placeholder for future cleanup.
        Chroma PersistentClient currently doesn't require an explicit close.
        """
        self.client = None
        self.collection = None