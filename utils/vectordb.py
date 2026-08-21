import chromadb
from chromadb.config import Settings


class VectorDB:
    """
    ChromaDB vector collection wrapper with batch document indexing and similarity search.
    """

    def __init__(self, db_path: str, collection_name: str = "documents"):
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
        batch_size: int = 200
    ):
        """Add chunks and embeddings in batches."""
        total = len(chunks)
        for i in range(0, total, batch_size):
            batch_chunks = chunks[i : i + batch_size]
            batch_embeddings = embeddings[i : i + batch_size]

            ids = [f"doc_{chunk.get('chunk_index', i + idx)}" for idx, chunk in enumerate(batch_chunks)]
            documents = [chunk["text"] for chunk in batch_chunks]
            metadatas = [
                {
                    "page": int(chunk.get("page", 1)),
                    "source": str(chunk.get("source", "Document")),
                    "chunk_index": int(chunk.get("chunk_index", i + idx))
                }
                for idx, chunk in enumerate(batch_chunks)
            ]

            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=batch_embeddings,
                metadatas=metadatas
            )

    def search(self, query_embedding: list[float], k: int = 5) -> dict:
        """
        Search for top-k nearest neighbors.
        Returns Chroma query result dictionary.
        """
        count = self.collection.count()
        if count == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        actual_k = min(k, count)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k
        )
        return results

    def count(self) -> int:
        """Return total number of vectors in collection."""
        return self.collection.count()