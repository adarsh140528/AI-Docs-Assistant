import os
import json
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import (
    INDEXES_DIR,
    UPLOADS_DIR,
    GROQ_API_KEY,
    GROQ_MODEL,
    EMBEDDING_MODEL,
    RERANKER_MODEL,
    PORT,
)
from services.index_service import IndexService
from services.knowledge_base_manager import KnowledgeBaseManager
from services.rag_service import RAGService
from utils.llm import LLM
from utils.embedder import Embedder
from utils.reranker import Reranker

app = FastAPI(title="Adorush AI Assistant API", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from dotenv import load_dotenv

# Services
kb_manager = KnowledgeBaseManager()
embedder_singleton = Embedder()
reranker_singleton = Reranker()

def get_rag_service():
    load_dotenv(override=True)
    llm = LLM()
    return RAGService(
        llm=llm,
        embedder=embedder_singleton,
        reranker=reranker_singleton
    )

# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------

@app.get("/api/status")
def get_status():
    load_dotenv(override=True)
    llm = LLM()
    indexes = kb_manager.list_indexes()
    return {
        "status": "online",
        "provider": llm.provider,
        "is_configured": llm.provider != "unconfigured",
        "model": getattr(llm, "model_name", "None"),
        "embedder": EMBEDDING_MODEL,
        "reranker": RERANKER_MODEL,
        "knowledge_base_count": len(indexes)
    }

@app.get("/api/knowledge-bases")
def list_knowledge_bases():
    indexes = kb_manager.list_indexes()
    result = []
    for name in indexes:
        meta = kb_manager.get_metadata(name)
        result.append({
            "name": name,
            "documents": meta.get("documents", []),
            "pages": meta.get("pages", 0),
            "chunks": meta.get("chunks", 0),
            "created_at": meta.get("created_at", "Unknown")
        })
    return {"knowledge_bases": result}

@app.delete("/api/knowledge-bases/{name}")
def delete_knowledge_base(name: str):
    success = kb_manager.delete_index(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Knowledge Base '{name}' not found.")
    return {"message": f"Knowledge Base '{name}' deleted successfully."}

@app.post("/api/ingest")
async def ingest_documents(
    files: list[UploadFile] = File(...),
    custom_name: Optional[str] = Form(None)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    saved_tuples = []

    for f in files:
        safe_name = os.path.basename(f.filename)
        dest_path = os.path.join(UPLOADS_DIR, safe_name)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved_tuples.append((dest_path, safe_name))

    try:
        index_service = IndexService(embedder=embedder_singleton)
        stats = index_service.build(
            files=saved_tuples,
            custom_name=custom_name
        )
        return {
            "success": True,
            "index": stats["index"],
            "documents": stats["documents"],
            "pages": stats["pages"],
            "chunks": stats["chunks"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatPayload(BaseModel):
    query: str
    history: list[dict] = []
    indexes: list[str] = []
    top_k: int = 5

@app.post("/api/chat/stream")
def chat_stream(payload: ChatPayload):
    history_tuples = []
    for msg in payload.history[-6:]:
        role = "User" if msg.get("role") == "user" else "Assistant"
        history_tuples.append(f"{role}: {msg.get('content', '')}")

    def event_generator():
        try:
            rag_service = get_rag_service()
            stream_gen, sources = rag_service.stream(
                question=payload.query,
                history=history_tuples,
                indexes=payload.indexes,
                top_k=payload.top_k
            )

            # 1. Send sources metadata first
            sources_json = json.dumps({"type": "sources", "sources": sources})
            yield f"data: {sources_json}\n\n"

            # 2. Stream token chunks
            for token in stream_gen:
                if token:
                    data_json = json.dumps({"type": "token", "content": token})
                    yield f"data: {data_json}\n\n"

            # 3. Send done event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            err_json = json.dumps({"type": "error", "error": str(e)})
            yield f"data: {err_json}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/page-preview")
def get_page_preview(index: str, source: str, page: int):
    pages_file = os.path.join(INDEXES_DIR, index, "pages.json")
    if not os.path.exists(pages_file):
        raise HTTPException(status_code=404, detail="Page archive not found.")

    try:
        with open(pages_file, "r", encoding="utf-8") as f:
            pages_map = json.load(f)

        lookup_key = f"{source}__page_{page}"
        text = pages_map.get(lookup_key, pages_map.get(str(page), "Text unavailable."))
        return {"index": index, "source": source, "page": page, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static directory for frontend
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
