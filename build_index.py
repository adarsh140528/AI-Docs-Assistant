import os
from config import PDF_PATH
from services.index_service import IndexService


def main():
    print("=" * 60)
    print("Building Default Knowledge Base from PDF")
    print("=" * 60)

    if not os.path.exists(PDF_PATH):
        print(f"File {PDF_PATH} does not exist. Please specify a valid document.")
        return

    index_service = IndexService()
    stats = index_service.build(
        files=PDF_PATH,
        custom_name="default_kb"
    )

    print("\n✅ Knowledge Base Successfully Created!")
    print(f"Index: {stats['index']}")
    print(f"Pages: {stats['pages']}")
    print(f"Chunks: {stats['chunks']}")


if __name__ == "__main__":
    main()