import os
import pickle
from collections import defaultdict
from utils.embedder import Embedder
from utils.vectordb import VectorDB
from config import (
    INDEXES_DIR,
    CURRENT_INDEX_FILE,
    DEFAULT_INDEX,
    TOP_K_RETRIEVAL,
)


class HybridRetriever:
    """
    Unified Hybrid Retriever combining:
    - ChromaDB (Dense Vector Search)
    - BM25 (Sparse Keyword Search)
    - Reciprocal Rank Fusion (RRF) for multi-index candidate scoring
    - In-memory collection caching
    """

    def __init__(self, embedder: Embedder = None):
        self.embedder = embedder or Embedder()
        self._db_cache = {}
        self._bm25_cache = {}

    def _load_index_components(self, index_name: str) -> tuple[VectorDB, any]:
        """Load and cache VectorDB and BM25 components for a given index."""
        if index_name in self._db_cache:
            return self._db_cache[index_name], self._bm25_cache.get(index_name)

        index_path = os.path.join(INDEXES_DIR, index_name)
        if not os.path.exists(index_path):
            return None, None

        db = VectorDB(index_path)
        self._db_cache[index_name] = db

        bm25 = None
        bm25_path = os.path.join(index_path, "bm25.pkl")
        if os.path.exists(bm25_path):
            try:
                with open(bm25_path, "rb") as f:
                    bm25 = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load BM25 for {index_name}: {e}")

        self._bm25_cache[index_name] = bm25
        return db, bm25

    def get_current_index(self) -> str:
        """Get the active index name from disk."""
        if not os.path.exists(CURRENT_INDEX_FILE):
            return DEFAULT_INDEX
        try:
            with open(CURRENT_INDEX_FILE, "r", encoding="utf-8") as f:
                current = f.read().strip()
            return current or DEFAULT_INDEX
        except Exception:
            return DEFAULT_INDEX

    def retrieve(
        self,
        question: str,
        indexes: list[str] = None,
        k: int = None,
        rrf_k: int = 60
    ) -> tuple[list[str], list[dict]]:
        """
        Unified Hybrid Retrieval across one or multiple knowledge bases.
        Returns: (merged_documents, sources)
        """
        target_indexes = indexes if indexes else [self.get_current_index()]
        target_k = k or TOP_K_RETRIEVAL

        query_embedding = self.embedder.embed(question)

        # Mapping: unique_doc_text -> {"doc": str, "source": dict, "rrf_score": float}
        candidate_map = {}
        rrf_scores = defaultdict(float)

        for index_name in target_indexes:
            db, bm25 = self._load_index_components(index_name)
            if db is None:
                continue

            # 1. Dense Vector Search
            vector_results = db.search(query_embedding=query_embedding, k=target_k)
            vector_docs = vector_results.get("documents", [[]])[0]
            vector_metas = vector_results.get("metadatas", [[]])[0]

            for rank, (doc, meta) in enumerate(zip(vector_docs, vector_metas)):
                if not doc:
                    continue
                doc_key = doc.strip()
                rrf_scores[doc_key] += 1.0 / (rrf_k + rank + 1)
                if doc_key not in candidate_map:
                    candidate_map[doc_key] = {
                        "doc": doc,
                        "source": {
                            "page": meta.get("page", 1),
                            "source": meta.get("source", "Document"),
                            "index": index_name,
                            "type": "dense"
                        }
                    }

            # 2. Sparse BM25 Search
            if bm25 is not None:
                bm25_docs, bm25_metas = bm25.search(question, k=target_k)
                for rank, (doc, meta) in enumerate(zip(bm25_docs, bm25_metas)):
                    if not doc:
                        continue
                    doc_key = doc.strip()
                    rrf_scores[doc_key] += 1.0 / (rrf_k + rank + 1)
                    if doc_key not in candidate_map:
                        candidate_map[doc_key] = {
                            "doc": doc,
                            "source": {
                                "page": meta.get("page", 1),
                                "source": meta.get("source", "Document"),
                                "index": index_name,
                                "type": "sparse"
                            }
                        }

        # Sort candidates by combined RRF score
        sorted_candidates = sorted(
            candidate_map.keys(),
            key=lambda key: rrf_scores[key],
            reverse=True
        )

        merged_documents = []
        sources = []

        for key in sorted_candidates[: target_k * 2]:
            item = candidate_map[key]
            merged_documents.append(item["doc"])
            source_info = item["source"]
            source_info["rrf_score"] = rrf_scores[key]
            sources.append(source_info)

        return merged_documents, sources

    def unload_index(self, index_name: str):
        """Unload and close a specific index from cache."""
        if index_name in self._db_cache:
            db = self._db_cache.pop(index_name)
            if db:
                db.close()
        if index_name in self._bm25_cache:
            self._bm25_cache.pop(index_name)

    def clear_cache(self):
        """Clear cached VectorDB and BM25 instances."""
        for name in list(self._db_cache.keys()):
            self.unload_index(name)
        self._db_cache.clear()
        self._bm25_cache.clear()


# Backward-compatible alias
Retriever = HybridRetriever