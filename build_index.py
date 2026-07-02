from config import PDF_PATH
from services.index_service import IndexService


def main():

    IndexService().build(
        PDF_PATH,
        "adorush.pdf"
    )


if __name__ == "__main__":
    main()