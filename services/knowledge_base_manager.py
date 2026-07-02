import os
from datetime import datetime

from config import (
    INDEXES_DIR,
    CURRENT_INDEX_FILE,
)


class KnowledgeBaseManager:

    def __init__(self):
        os.makedirs(INDEXES_DIR, exist_ok=True)

    def create_name(self, pdf_filename):
        """
        Example:
        API_Guide.pdf
        ->
        API_Guide_20260701_201523
        """

        base = os.path.splitext(pdf_filename)[0]

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        return f"{base}_{timestamp}"

    def set_current(self, name):

        with open(
            CURRENT_INDEX_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(name)

    def get_current(self):

        if not os.path.exists(CURRENT_INDEX_FILE):
            return None

        with open(
            CURRENT_INDEX_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().strip()

    def list_indexes(self):

        folders = []

        for item in os.listdir(INDEXES_DIR):

            path = os.path.join(
                INDEXES_DIR,
                item
            )

            if os.path.isdir(path):

                # Skip default knowledge base
                if item.lower() == "default":
                    continue

                folders.append(item)

        folders.sort(reverse=True)

        return folders