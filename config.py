# Default PDF (used only by build_index.py)
PDF_PATH = "docs/adorush.pdf"

# Text Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Models
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:3b"

# -------------------------------------------------
# Index Configuration
# -------------------------------------------------

# Folder where ALL knowledge bases will be stored
INDEXES_DIR = "indexes"

# Stores which knowledge base is currently active
CURRENT_INDEX_FILE = "indexes/current.txt"

# Default index name
DEFAULT_INDEX = "default"