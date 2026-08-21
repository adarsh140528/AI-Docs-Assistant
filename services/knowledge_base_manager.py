import os
import json
import shutil
import re
from datetime import datetime
from config import INDEXES_DIR, CURRENT_INDEX_FILE, DEFAULT_INDEX


class KnowledgeBaseManager:
    """
    Manages Knowledge Base lifecycles (Creation, Listing, Metadata Inspection, Deletion).
    """

    def __init__(self):
        os.makedirs(INDEXES_DIR, exist_ok=True)

    def sanitize_name(self, name: str) -> str:
        """Sanitize a user-provided KB name for safe directory creation."""
        clean = re.sub(r"[^\w\-_]", "_", name.strip())
        return clean if clean else "kb"

    def create_name(self, base_name: str) -> str:
        """
        Example: API_Guide.pdf -> API_Guide_20260821_182500
        """
        clean_base = self.sanitize_name(os.path.splitext(base_name)[0])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{clean_base}_{timestamp}"

    def set_current(self, name: str):
        """Set the active Knowledge Base."""
        with open(CURRENT_INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(name)

    def get_current(self) -> str:
        """Get the active Knowledge Base name."""
        if not os.path.exists(CURRENT_INDEX_FILE):
            return None
        try:
            with open(CURRENT_INDEX_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return content if content else None
        except Exception:
            return None

    def list_indexes(self) -> list[str]:
        """List all available knowledge base index names."""
        folders = []
        if not os.path.exists(INDEXES_DIR):
            return []

        for item in os.listdir(INDEXES_DIR):
            path = os.path.join(INDEXES_DIR, item)
            if os.path.isdir(path):
                folders.append(item)

        folders.sort(reverse=True)
        return folders

    def get_metadata(self, index_name: str) -> dict:
        """Read and return metadata for a specific Knowledge Base."""
        index_path = os.path.join(INDEXES_DIR, index_name)
        meta_file = os.path.join(index_path, "metadata.json")

        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Fallback inspection if metadata.json is missing
        pages_file = os.path.join(index_path, "pages.json")
        total_pages = 0
        if os.path.exists(pages_file):
            try:
                with open(pages_file, "r", encoding="utf-8") as f:
                    pages = json.load(f)
                    total_pages = len(pages)
            except Exception:
                pass

        return {
            "name": index_name,
            "documents": ["Unknown"],
            "pages": total_pages,
            "chunks": 0,
            "created_at": "Unknown",
            "provider": "Unknown"
        }

    def delete_index(self, index_name: str) -> bool:
        """Safely delete a knowledge base from disk."""
        index_path = os.path.join(INDEXES_DIR, index_name)
        if os.path.exists(index_path):
            try:
                shutil.rmtree(index_path)
                # If deleted KB was the current one, reset current
                if self.get_current() == index_name:
                    indexes = self.list_indexes()
                    if indexes:
                        self.set_current(indexes[0])
                    else:
                        if os.path.exists(CURRENT_INDEX_FILE):
                            os.remove(CURRENT_INDEX_FILE)
                return True
            except Exception as e:
                print(f"Error deleting index {index_name}: {e}")
                return False
        return False