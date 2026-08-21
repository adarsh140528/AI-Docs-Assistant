from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """
    Intelligent text chunker using recursive character splitting.
    Preserves sentence boundaries, paragraphs, and document metadata.
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
            length_function=len,
        )

    def split(self, pages: list[dict]) -> list[dict]:
        """
        Split list of page dicts into enriched chunk dicts:
        [
            {
                "page": int,
                "text": str,
                "source": str,
                "chunk_index": int
            },
            ...
        ]
        """
        chunks = []
        chunk_counter = 0

        for page_data in pages:
            text = page_data.get("text", "").strip()
            page_number = page_data.get("page", 1)
            source_file = page_data.get("source", "Document")

            if not text or len(text) < 20:
                continue

            split_texts = self.splitter.split_text(text)

            for snippet in split_texts:
                clean_snippet = snippet.strip()
                if len(clean_snippet) >= 30:
                    chunks.append({
                        "page": page_number,
                        "text": clean_snippet,
                        "source": source_file,
                        "chunk_index": chunk_counter
                    })
                    chunk_counter += 1

        return chunks