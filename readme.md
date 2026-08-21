# 🤖 Adorush AI • Enterprise Documentation Assistant

An enterprise-grade, cloud-deployable **Retrieval-Augmented Generation (RAG)** platform powered by **Groq Llama 3.3 70B** and local **SentenceTransformers** embeddings.

---

## ✨ Features

- 🎨 **Premier Glassmorphism Web App**: Sleek HTML5 / CSS3 / JavaScript interface with dark theme, responsive sidebar, and animated components.
- ⚡ **Groq Llama 3.3 70B**: Lightning-fast, static LLM inference via Groq API.
- 🧠 **100% Offline / Zero-Cost Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` runs locally on CPU with zero rate limits, zero API costs, and zero 404 errors.
- 🔍 **Hybrid Retrieval + Reciprocal Rank Fusion (RRF)**: Merges ChromaDB dense vector search with BM25Okapi sparse lexical keyword search.
- 🎯 **Cross-Encoder Reranker**: High-precision context scoring using `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- 📄 **Multi-Format Ingestion**: Ingest `.pdf`, `.docx`, `.txt`, `.md`, and `.csv` files into organized, custom-named Knowledge Bases.
- 📑 **Source Attribution & Full-Page Inspector**: In-line citation pills with relevance chips and a slide-out drawer to inspect supporting page text.
- 🔒 **Secure Environment Configuration**: API keys are managed purely via `.env` on the backend without any frontend key exposure.
- 📥 **Export Chat History**: One-click download of conversation transcripts to Markdown.

---

## 🏗️ Architecture

```
        Uploaded Documents (.pdf, .docx, .txt, .md)
                            │
                            ▼
                   DocLoader & Cleaner
                            │
                            ▼
              Recursive Character Chunking
                            │
                            ▼
           Local Embeddings (all-MiniLM-L6-v2)
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
        ChromaDB                       BM25 Index
             │                             │
             └──────────────┬──────────────┘
                            │
                    User Question
                            │
                            ▼
             Conversational Query Rewriter
                            │
                            ▼
          Hybrid Retrieval + Reciprocal Rank Fusion
                            │
                            ▼
                 Cross-Encoder Reranker
                            │
                            ▼
              Prompt with Source Citations
                            │
                            ▼
                 Groq Llama 3.3 70B
                            │
                            ▼
             Token Streaming & Source Pills
```

---

## 📂 Project Structure

```
AI-Docs-Assistant/
├── static/
│   ├── index.html          # Web application structure
│   ├── style.css           # Glassmorphism design system
│   └── app.js              # Real-time streaming & UI logic
├── services/
│   ├── index_service.py    # Multi-file chunking, embedding & indexing
│   ├── knowledge_base_manager.py # Knowledge base lifecycle management (CRUD)
│   └── rag_service.py      # Conversational RAG pipeline orchestrator
├── utils/
│   ├── bm25.py             # BM25 sparse keyword retrieval
│   ├── chunker.py          # RecursiveCharacterTextSplitter
│   ├── doc_loader.py       # Multi-format document loader (PDF, DOCX, TXT, MD)
│   ├── embedder.py         # Local SentenceTransformer embeddings
│   ├── llm.py              # Groq Llama 3.3 inference & streaming
│   ├── prompt.py           # Grounded prompt templates & query condensation
│   ├── reranker.py         # Cross-Encoder MiniLM reranking
│   ├── retriever.py        # Unified Hybrid Retriever with RRF & caching
│   └── vectordb.py         # ChromaDB vector database wrapper
├── server.py               # FastAPI backend & static file server
├── config.py               # Central environment configuration
├── build_index.py          # CLI indexing script
├── chat.py                 # CLI chat script
├── requirements.txt        # Production dependencies
├── .env.example            # Environment variables template
└── README.md
```

---

## 🚀 Quickstart & Installation

### 1. Clone & Setup Virtual Environment

```bash
git clone https://github.com/adarsh140528/AI-Docs-Assistant.git
cd AI-Docs-Assistant

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux / macOS)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and paste your free Groq API key:

```bash
cp .env.example .env
```

Inside `.env`:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
PORT=8000
```
*(Get a free Groq API key in under 1 minute at [https://console.groq.com/keys](https://console.groq.com/keys))*

### 4. Run the Server

```bash
python server.py
```

Open your browser at **[http://localhost:8000](http://localhost:8000)**.

---

## 🌐 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Health check & model status |
| `GET` | `/api/knowledge-bases` | List all available Knowledge Bases with metadata |
| `DELETE` | `/api/knowledge-bases/{name}` | Delete a Knowledge Base |
| `POST` | `/api/ingest` | Multipart upload to parse, chunk, embed, and index documents |
| `POST` | `/api/chat/stream` | Server-Sent Events (SSE) streaming chat endpoint with citations |
| `GET` | `/api/page-preview` | Fetch original full-page document text for source inspection |

---

## 📄 License

This project is licensed under the MIT License.