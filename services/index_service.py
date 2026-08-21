import os
import json
import pickle
from datetime import datetime
from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    INDEXES_DIR,
    EMBEDDING_PROVIDER,
)
from services.knowledge_base_manager import KnowledgeBaseManager
from utils.doc_loader import DocLoader, clean_text
from utils.chunker import TextChunker
from utils.embedder import Embedder
from utils.vectordb import VectorDB
from utils.bm25 import BM25Retriever


class IndexService:
    """
    Builds and persists Knowledge Bases from single or multiple documents
    with batch embeddings, ChromaDB, and BM25.
    """

    def __init__(self, embedder: Embedder = None):
        self.kb = KnowledgeBaseManager()
        self.embedder = embedder or Embedder()

    def build(
        self,
        files: list[tuple[str, str]] | str,
        custom_name: str = None,
        pdf_filename: str = None,
        pdf_path: str = None,
        progress_callback = None
    ) -> dict:
        """
        Build a Knowledge Base from one or more uploaded files.
        - `files`: list of `(file_path, original_filename)` or single file_path.
        - `progress_callback`: optional callable `(fraction: float, message: str)`
        """
        def update_progress(frac: float, msg: str):
            if progress_callback:
                progress_callback(frac, msg)
            print(f"[{int(frac * 100)}%] {msg}")

        # Normalize input files
        file_list = []
        if isinstance(files, list):
            file_list = files
        elif pdf_path and pdf_filename:
            file_list = [(pdf_path, pdf_filename)]
        elif isinstance(files, str):
            file_list = [(files, pdf_filename or os.path.basename(files))]

        if not file_list:
            raise ValueError("No files provided for indexing.")

        update_progress(0.05, "Initializing Knowledge Base...")

        # Determine Knowledge Base Name
        if custom_name and custom_name.strip():
            index_name = self.kb.sanitize_name(custom_name)
        else:
            primary_name = file_list[0][1]
            index_name = self.kb.create_name(primary_name)

        index_path = os.path.join(INDEXES_DIR, index_name)
        os.makedirs(index_path, exist_ok=True)

        # 1. Load and Extract Pages from All Documents
        update_progress(0.15, "Extracting text from uploaded documents...")
        all_pages = []
        doc_names = []
        page_map = {}

        for fpath, fname in file_list:
            doc_names.append(fname)
            loader = DocLoader(fpath, original_filename=fname)
            doc_pages = loader.load()

            for p in doc_pages:
                p["text"] = clean_text(p["text"])
                all_pages.append(p)
                # Store in page_map for UI full-page preview lookup
                lookup_key = f"{fname}__page_{p['page']}"
                page_map[lookup_key] = p["text"]
                # Also store single-page key for backward compatibility
                page_map[str(p["page"])] = p["text"]

        # Persist full pages lookup
        with open(os.path.join(index_path, "pages.json"), "w", encoding="utf-8") as f:
            json.dump(page_map, f, ensure_ascii=False, indent=2)

        # 2. Chunk Texts
        update_progress(0.35, f"Chunking {len(all_pages)} pages into semantic passages...")
        chunker = TextChunker(chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        chunks = chunker.split(all_pages)

        if not chunks:
            # Fallback if no text extracted
            chunks = [{
                "page": 1,
                "text": "No text could be extracted from the document.",
                "source": file_list[0][1],
                "chunk_index": 0
            }]

        # 3. Generate Embeddings in Batches
        update_progress(0.50, f"Generating cloud vector embeddings ({len(chunks)} chunks)...")
        chunk_texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed_batch(chunk_texts, batch_size=32)

        # 4. Save ChromaDB Vector Collection
        update_progress(0.75, "Saving vector embeddings to ChromaDB...")
        db = VectorDB(index_path)
        db.add_documents(chunks, embeddings)

        # 5. Build and Save BM25 Index
        update_progress(0.85, "Building BM25 sparse keyword index...")
        bm25 = BM25Retriever()
        bm25.build(chunks)
        with open(os.path.join(index_path, "bm25.pkl"), "wb") as f:
            pickle.dump(bm25, f)

        # 6. Save Metadata & Activate
        update_progress(0.95, "Finalizing Knowledge Base metadata...")
        metadata = {
            "name": index_name,
            "documents": doc_names,
            "pages": len(all_pages),
            "chunks": len(chunks),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "provider": self.embedder.provider,
            "embedding_model": self.embedder.model_name,
        }

        with open(os.path.join(index_path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        self.kb.set_current(index_name)
        update_progress(1.0, f"Knowledge Base '{index_name}' built successfully!")

        return {
            "index": index_name,
            "documents": doc_names,
            "pages": len(all_pages),
            "chunks": len(chunks)
        }