from config import LLM_MODEL
from utils.multi_retriever import MultiRetriever
from utils.retriever import Retriever
from utils.prompt import PromptBuilder
from utils.llm import LLM
from utils.reranker import Reranker


class RAGService:

    def __init__(self):
        self.llm = LLM(LLM_MODEL)
        self.reranker = Reranker()
        self.reload()

    def reload(self):
        """Reload the vector database"""
        self.retriever = Retriever()
        self.multi_retriever = MultiRetriever()

    # -----------------------------------------
    # Normal Response
    # -----------------------------------------

    def ask(self, question, history=None,indexes=None):

        if indexes and len(indexes) > 1:
            documents, metadata = self.multi_retriever.retrieve(
                question,
                indexes
            )
        else:
            documents, metadata = self.retriever.retrieve(
                question
            )

        # -----------------------------------------
        # Rerank Documents + Sources
        # -----------------------------------------

        documents, metadata = self.reranker.rerank(
            question=question,
            documents=documents,
            sources=metadata,
            top_k=5
        )

        prompt = PromptBuilder.build(
            question=question,
            documents=documents,
            history=history
        )

        answer = self.llm.generate(prompt)

        return answer, metadata

    # -----------------------------------------
    # Streaming Response
    # -----------------------------------------

    def stream(self, question, history=None,indexes=None):

        if indexes and len(indexes) > 1:
            documents, metadata = self.multi_retriever.retrieve(
                question,
                indexes
            )
        else:
            documents, metadata = self.retriever.retrieve(
                question
            )

        # -----------------------------------------
        # Rerank Documents + Sources
        # -----------------------------------------

        documents, metadata = self.reranker.rerank(
            question=question,
            documents=documents,
            sources=metadata,
            top_k=5
        )

        prompt = PromptBuilder.build(
            question=question,
            documents=documents,
            history=history
        )

        return self.llm.stream(prompt), metadata