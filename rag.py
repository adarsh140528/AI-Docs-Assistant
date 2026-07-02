from services.rag_service import RAGService

rag = RAGService()


def ask(
    question,
    history=None,
    indexes=None
):
    return rag.ask(
        question,
        history,
        indexes
    )


def stream(
    question,
    history=None,
    indexes=None
):
    return rag.stream(
        question,
        history,
        indexes
    )


def reload():
    global rag

    del rag

    rag = RAGService()