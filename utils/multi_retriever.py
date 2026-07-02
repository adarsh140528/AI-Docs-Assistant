import os
import pickle

from utils.embedder import Embedder
from utils.vectordb import VectorDB

from config import (
    EMBEDDING_MODEL,
    INDEXES_DIR,
)


class MultiRetriever:

    def __init__(self):

        self.embedder = Embedder(
            EMBEDDING_MODEL
        )

    def load_database(
        self,
        index_name
    ):

        index_path = os.path.join(
            INDEXES_DIR,
            index_name
        )

        db = VectorDB(index_path)

        bm25 = None

        bm25_path = os.path.join(
            index_path,
            "bm25.pkl"
        )

        if os.path.exists(bm25_path):

            with open(
                bm25_path,
                "rb"
            ) as f:

                bm25 = pickle.load(f)

        return db, bm25

    def retrieve(
        self,
        question,
        indexes,
        k=5
    ):

        embedding = self.embedder.embed(question)

        all_documents = []
        all_sources = []

        for index in indexes:

            db, bm25 = self.load_database(index)

            # -----------------------------
            # Vector Search
            # -----------------------------

            results = db.search(
                query_embedding=embedding,
                k=k
            )

            vector_docs = results["documents"][0]
            vector_meta = results["metadatas"][0]

            # Add vector results
            for doc, meta in zip(
                vector_docs,
                vector_meta
            ):

                all_documents.append(doc)

                all_sources.append(
                    {
                        "page": meta["page"],
                        "content": doc,
                        "index": index
                    }
                )

            # -----------------------------
            # BM25 Search
            # -----------------------------

            if bm25 is not None:

                docs, metas = bm25.search(
                    question,
                    k=k
                )

                for doc, meta in zip(
                    docs,
                    metas
                ):

                    all_documents.append(doc)

                    all_sources.append(
                        {
                            "page": meta["page"],
                            "content": doc,
                            "index": index
                        }
                    )

        return all_documents, all_sources