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

## 🚀 Easy Cloud Deployment (Fixes 502 Bad Gateway)

Why does **502 Bad Gateway** usually happen on cloud platforms (Render, Railway, Heroku, Fly.io)?
1. **Port binding**: Cloud platforms assign a dynamic `$PORT` (e.g. `10000`). If your app binds to `127.0.0.1:8000`, the cloud proxy cannot reach it.
2. **Missing Health Check**: Cloud load balancers probe `/health` or `/api/health` before routing traffic.
3. **PyTorch Memory Exhaustion**: Running multiple Gunicorn workers loads multiple PyTorch models into RAM, triggering OOM (Out Of Memory) SIGKILL.
4. **Worker Timeout**: Model initialization can take >30s on cold start without keep-alive timeouts.

This repository includes pre-configured **`Procfile`**, **`render.yaml`**, **`Dockerfile`**, and **`start.sh`** to make deployments 100% reliable.

### Option 1: Deploy to Render (Recommended - Free & Easy)
1. Push this repository to your GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) -> **New Web Service**.
3. Connect your repository.
4. Configure the settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements-cpu.txt` (or `pip install -r requirements.txt`)
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 75`
   - **Health Check Path**: `/health`
5. Add Environment Variables:
   - `GROQ_API_KEY`: `gsk_your_groq_api_key_here`
6. Click **Deploy Web Service**!

### Option 2: Deploy with Docker (Any Cloud / VPS / Hugging Face)
```bash
# Build the Docker image (CPU optimized with pre-cached models)
docker build -t ai-docs-assistant .

# Run container
docker run -d -p 8000:8000 -e GROQ_API_KEY="your_api_key" ai-docs-assistant
```

### Option 3: Deploy to Railway
1. Click **New Project** -> **Deploy from GitHub repo**.
2. Railway will automatically detect the `Procfile` and `Dockerfile`.
3. Set the `GROQ_API_KEY` variable in the Railway project dashboard.

---

## 🌐 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` / `/ping` | Lightweight health check probe for load balancers |
| `GET` | `/api/status` | System configuration & model status |
| `GET` | `/api/knowledge-bases` | List all available Knowledge Bases with metadata |
| `DELETE` | `/api/knowledge-bases/{name}` | Delete a Knowledge Base |
| `POST` | `/api/ingest` | Multipart upload to parse, chunk, embed, and index documents |
| `POST` | `/api/chat/stream` | Server-Sent Events (SSE) streaming chat endpoint with citations |
| `GET` | `/api/page-preview` | Fetch original full-page document text for source inspection |

---

## 📄 License

This project is licensed under the MIT License.