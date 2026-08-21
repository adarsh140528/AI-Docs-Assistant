from services.rag_service import RAGService

# Singleton instance
rag = RAGService()


def ask(question: str, history: list[str] = None, indexes: list[str] = None, top_k: int = None):
    return rag.ask(question, history, indexes, top_k=top_k)


def stream(question: str, history: list[str] = None, indexes: list[str] = None, top_k: int = None):
    return rag.stream(question, history, indexes, top_k=top_k)


def reload():
    global rag
    rag.reload()