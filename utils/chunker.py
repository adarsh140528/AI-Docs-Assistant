class TextChunker:
    def __init__(self, chunk_size=1000, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, pages):
        chunks = []

        for page in pages:
            text = page["text"]
            page_number = page["page"]

            # Skip synthetic reference pages
            if "Extended Reference" in text:
                continue

            start = 0

            while start < len(text):
                end = start + self.chunk_size

                chunk = text[start:end].strip()

                # Skip empty chunks
                if len(chunk) < 50:
                    start += self.chunk_size - self.overlap
                    continue

                chunks.append({
                    "page": page_number,
                    "text": chunk
                })

                start += self.chunk_size - self.overlap

        return chunks