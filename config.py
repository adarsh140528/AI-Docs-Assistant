import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Storage Directories
INDEXES_DIR = os.getenv("INDEXES_DIR", "indexes")
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")
CURRENT_INDEX_FILE = os.path.join(INDEXES_DIR, "current.txt")
DEFAULT_INDEX = "default"

# Text Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Static Groq LLM & Gemini API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_FALLBACK_MODEL = "groq/compound-mini"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Embedding & Reranker Configuration
# Options for EMBEDDING_PROVIDER: "local" (default offline) or "gemini" (cloud API for low-RAM deployment)
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# Retrieval Parameters
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", "5"))

# Server Port
PORT = int(os.getenv("PORT", "8000"))