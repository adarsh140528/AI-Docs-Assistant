import os
import pickle

from utils.embedder import Embedder
from utils.vectordb import VectorDB

from config import (
    EMBEDDING_MODEL,
    INDEXES_DIR,
    CURRENT_INDEX_FILE,
    DEFAULT_INDEX,
)


class Retriever:

    def __init__(self):

        self.embedder = Embedder(EMBEDDING_MODEL)

        self.index_path = self.get_current_index_path()

        self.db, self.bm25 = self.load_database(
            self.index_path
        )

    # ---------------------------------------
    # Load Database + BM25
    # ---------------------------------------

    def load_database(self, index_path):

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

    # ---------------------------------------
    # Current Knowledge Base
    # ---------------------------------------

    def get_current_index_path(self):

        if not os.path.exists(CURRENT_INDEX_FILE):

            return os.path.join(
                INDEXES_DIR,
                DEFAULT_INDEX
            )

        with open(
            CURRENT_INDEX_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            current = f.read().strip()

        if not current:
            current = DEFAULT_INDEX

        return os.path.join(
            INDEXES_DIR,
            current
        )

    # ---------------------------------------
    # Retrieve
    # ---------------------------------------

    def retrieve(
        self,
        question,
        k=5
    ):

        embedding = self.embedder.embed(question)

        vector_results = self.db.search(
            query_embedding=embedding,
            k=k
        )

        vector_documents = vector_results["documents"][0]
        vector_metadatas = vector_results["metadatas"][0]

        bm25_documents = []
        bm25_metadatas = []

        if self.bm25 is not None:

            bm25_documents, bm25_metadatas = self.bm25.search(
                question,
                k=k
            )

        merged_documents = []
        sources = []

        seen = set()

        for doc, meta in zip(
            vector_documents,
            vector_metadatas
        ):

            if doc not in seen:

                seen.add(doc)

                merged_documents.append(doc)

                sources.append(
                    {
                        "page": meta["page"],
                        "content": doc
                    }
                )

        for doc, meta in zip(
            bm25_documents,
            bm25_metadatas
        ):

            if doc not in seen:

                seen.add(doc)

                merged_documents.append(doc)

                sources.append(
                    {
                        "page": meta["page"],
                        "content": doc
                    }
                )

        return merged_documents, sources