from pypdf import PdfReader


def clean_text(text):

    if not text:
        return ""

    # Remove invalid Unicode surrogate characters
    text = (
        text.encode(
            "utf-16",
            "surrogatepass"
        ).decode(
            "utf-16",
            "ignore"
        )
    )

    # Remove any remaining invalid UTF-8 characters
    text = (
        text.encode(
            "utf-8",
            errors="ignore"
        ).decode(
            "utf-8"
        )
    )

    return text


class PDFLoader:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def load(self):

        reader = PdfReader(self.pdf_path)

        pages = []

        for i, page in enumerate(reader.pages):

            text = page.extract_text()

            if text:

                text = clean_text(text)

                pages.append(
                    {
                        "page": i + 1,
                        "text": text
                    }
                )

        return pages