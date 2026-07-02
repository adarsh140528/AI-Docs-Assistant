import os
import json

from utils.bm25 import BM25Retriever
import pickle
from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    INDEXES_DIR,
)

from services.knowledge_base_manager import KnowledgeBaseManager

from utils.pdf_loader import PDFLoader
from utils.chunker import TextChunker
from utils.embedder import Embedder
from utils.vectordb import VectorDB


def clean_text(text):
    
    if not text:
        return ""

    return (
        text.encode(
            "utf-16",
            "surrogatepass"
        ).decode(
            "utf-16",
            "ignore"
        )
    )


class IndexService:

    def __init__(self):
        self.kb = KnowledgeBaseManager()

    def build(self, pdf_path, pdf_filename):

        print("=" * 60)
        print("Building Knowledge Base")
        print("=" * 60)

        # ---------------------------------------
        # Create Knowledge Base Name
        # ---------------------------------------

        index_name = self.kb.create_name(pdf_filename)

        index_path = os.path.join(
            INDEXES_DIR,
            index_name
        )

        os.makedirs(
            index_path,
            exist_ok=True
        )

        # ---------------------------------------
        # Load PDF
        # ---------------------------------------

        loader = PDFLoader(pdf_path)

        pages = loader.load()

        # Clean extracted page text
        for page in pages:

            page["text"] = clean_text(
                page["text"]
            )

        # ---------------------------------------
        # Save Full Pages
        # ---------------------------------------

        page_map = {}

        for page in pages:

            page_map[
                str(page["page"])
            ] = page["text"]

        with open(
            os.path.join(
                index_path,
                "pages.json"
            ),
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                page_map,
                f,
                ensure_ascii=False,
                indent=4
            )

        print(f"Loaded Pages : {len(pages)}")

        # ---------------------------------------
        # Chunk
        # ---------------------------------------

        chunker = TextChunker(
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
        )

        chunks = chunker.split(pages)

        # Clean chunk text
        for chunk in chunks:

            chunk["text"] = clean_text(
                chunk["text"]
            )

        print(f"Created Chunks : {len(chunks)}")

        # ---------------------------------------
        # Embeddings
        # ---------------------------------------

        embedder = Embedder(
            EMBEDDING_MODEL
        )

        embeddings = []

        print("\nGenerating Embeddings...\n")

        total = len(chunks)

        for i, chunk in enumerate(chunks):

            embeddings.append(
                embedder.embed(chunk["text"])
            )

            if (i + 1) % 20 == 0 or (i + 1) == total:
                print(f"{i+1}/{total} completed")

        # ---------------------------------------
        # Save Chroma
        # ---------------------------------------

        db = VectorDB(index_path)

        db.add_documents(
            chunks,
            embeddings
        )

        # ---------------------------------------
        # Save BM25 Index
        # ---------------------------------------

        bm25 = BM25Retriever()

        bm25.build(chunks)

        with open(
            os.path.join(index_path, "bm25.pkl"),
            "wb"
        ) as f:

            pickle.dump(bm25, f)            

        
    
        # ---------------------------------------
        # Make Active
        # ---------------------------------------

        self.kb.set_current(index_name)

        print("\n✅ Knowledge Base Created!")
        

        return {
            "pages": len(pages),
            "chunks": len(chunks),
            "index": index_name
        }