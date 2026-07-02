# 🤖 Adorush AI Documentation Assistant

An AI-powered Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documentation and chat with it using a local Large Language Model (LLM).

The application combines **Semantic Search**, **BM25 Keyword Search**, and **Cross-Encoder Reranking** to provide accurate, context-aware answers with source attribution.

---

## ✨ Features

- 📄 Upload PDF documentation
- 📚 Automatic Knowledge Base creation
- 🤖 Chat with documents using Llama 3.2
- 🔍 Semantic Search using ChromaDB
- 🔤 BM25 Keyword Search
- ⚡ Hybrid Retrieval (Semantic + BM25)
- 🎯 Cross-Encoder Reranking
- 💬 Conversation Memory
- 🌊 Streaming AI Responses
- 📑 Source Attribution
- 📖 Full Page Source Preview
- 📚 Multiple Knowledge Base Search
- ⚡ Model Caching for faster startup
- 🖥️ Completely Local (No cloud APIs required)

---

# 🏗️ Architecture

```
                PDF Upload
                     │
                     ▼
               PDF Extraction
                (PyMuPDF)
                     │
                     ▼
              Text Chunking
                     │
                     ▼
     Embeddings (nomic-embed-text)
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    ChromaDB              BM25 Index
         │                       │
         └───────────┬───────────┘
                     ▼
             Hybrid Retrieval
                     │
                     ▼
        Cross-Encoder Reranker
                     │
                     ▼
        Prompt + Conversation History
                     │
                     ▼
         Llama 3.2 (Ollama)
                     │
                     ▼
          Streaming AI Response
                     │
                     ▼
            Source Attribution
```

---

# 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Streamlit | User Interface |
| Ollama | Local LLM Runtime |
| Llama 3.2 | Large Language Model |
| ChromaDB | Vector Database |
| nomic-embed-text | Embedding Model |
| BM25 | Keyword Retrieval |
| Cross Encoder MiniLM | Reranking |
| PyMuPDF | PDF Text Extraction |

---

# 📂 Project Structure

```
AI-Docs-Assistant/

├── assets/
├── docs/
├── indexes/
├── services/
│   ├── index_service.py
│   ├── knowledge_base_manager.py
│   └── rag_service.py
│
├── uploads/
├── utils/
│   ├── bm25.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── llm.py
│   ├── multi_retriever.py
│   ├── prompt.py
│   ├── reranker.py
│   ├── retriever.py
│   └── vectordb.py
│
├── app.py
├── rag.py
├── config.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/adarsh140528/AI-Docs-Assistant.git

cd AI-Docs-Assistant
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Install Ollama

Download from:

https://ollama.com

Pull required models:

```bash
ollama pull llama3.2
```

```bash
ollama pull nomic-embed-text
```

---

## Run Application

```bash
streamlit run app.py
```

---

# 💬 Usage

1. Upload one or more PDF documents.
2. Build a Knowledge Base.
3. Select one or multiple Knowledge Bases.
4. Ask questions about the uploaded documentation.
5. View AI-generated answers with supporting source pages.

---

# 📸 Screenshots

### Home

_Add screenshot here_

---

### Upload PDF

_Add screenshot here_

---

### Chat

_Add screenshot here_

---

### Source Attribution

_Add screenshot here_

---

### Multiple Knowledge Bases

_Add screenshot here_

---

# 🎯 Retrieval Pipeline

```
Question
    │
    ▼
Embedding
    │
    ▼
Semantic Search (ChromaDB)
    │
    ▼
BM25 Search
    │
    ▼
Merge Results
    │
    ▼
Cross Encoder Reranker
    │
    ▼
Top Context
    │
    ▼
Llama 3.2
    │
    ▼
Streaming Answer
```

---

# 📈 Key Features

- Hybrid Retrieval
- Retrieval-Augmented Generation (RAG)
- Multi Knowledge Base Support
- Streaming Responses
- Conversation Memory
- Cross Encoder Reranking
- Source Attribution
- Local AI Inference
- Full Page Preview
- Modular Architecture

---

# 🔮 Future Improvements

- Docker Support
- FastAPI Backend
- Authentication
- Cloud Deployment
- REST API
- OCR Support for Scanned PDFs

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Adarsh Rasal**

GitHub: https://github.com/adarsh140528

LinkedIn: https://www.linkedin.com/in/adarsh-rasal-a995922a9/

Portfolio: https://adarsh-rasal.vercel.app/

---

⭐ If you found this project useful, consider giving it a star on GitHub!