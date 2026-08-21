from typing import Generator
from config import TOP_K_RERANK
from utils.retriever import HybridRetriever
from utils.prompt import PromptBuilder
from utils.llm import LLM
from utils.embedder import Embedder
from utils.reranker import Reranker


class RAGService:
    """
    Orchestrates the entire Conversational RAG pipeline:
    1. Conversational Query Rewriting (for multi-turn follow-ups)
    2. Hybrid Dense + Sparse Retrieval with RRF
    3. Cross-Encoder Reranking
    4. Grounded Prompt Assembly
    5. Streaming & Batch Generation with Cited Source Attribution
    """

    def __init__(
        self,
        llm: LLM = None,
        embedder: Embedder = None,
        reranker: Reranker = None
    ):
        self.embedder = embedder or Embedder()
        self.llm = llm or LLM()
        self.reranker = reranker or Reranker()
        self.retriever = HybridRetriever(embedder=self.embedder)

    def reload(self):
        """Reload and clear in-memory retriever caches."""
        self.retriever.clear_cache()

    def rewrite_query_if_needed(self, question: str, history: list[str] = None) -> str:
        """
        If multi-turn history exists and the question looks like a follow-up,
        rewrite into a standalone search query.
        """
        if not history or len(history) == 0:
            return question

        # If question is already long or doesn't have pronouns, it might be standalone
        try:
            rewrite_prompt = PromptBuilder.build_query_condensation_prompt(question, history)
            rewritten = self.llm.generate(rewrite_prompt)
            clean_rewritten = rewritten.strip().strip('"').strip("'")
            if clean_rewritten and len(clean_rewritten) < 300 and "Error" not in clean_rewritten:
                return clean_rewritten
        except Exception as e:
            print(f"Query rewriting fallback: {e}")
        return question

    def _prepare_context(
        self,
        question: str,
        history: list[str] = None,
        indexes: list[str] = None,
        top_k: int = None
    ) -> tuple[str, list[dict], str, str]:
        """Internal helper for retrieval, reranking, and prompt construction."""
        # 1. Condense conversational query if history exists
        search_query = self.rewrite_query_if_needed(question, history)

        # 2. Hybrid Retrieval (Dense + BM25 with RRF)
        raw_documents, raw_sources = self.retriever.retrieve(
            question=search_query,
            indexes=indexes
        )

        # 3. Cross-Encoder Reranking
        k = top_k or TOP_K_RERANK
        reranked_docs, reranked_sources, scores = self.reranker.rerank(
            question=search_query,
            documents=raw_documents,
            sources=raw_sources,
            top_k=k
        )

        # 4. Build Structured Prompts
        system_prompt, user_prompt = PromptBuilder.build_rag_prompt(
            question=question,
            documents=reranked_docs,
            sources=reranked_sources,
            history=history
        )

        return search_query, reranked_sources, system_prompt, user_prompt

    def ask(
        self,
        question: str,
        history: list[str] = None,
        indexes: list[str] = None,
        top_k: int = None
    ) -> tuple[str, list[dict]]:
        """Synchronous RAG response with source attribution."""
        search_query, sources, system_prompt, user_prompt = self._prepare_context(
            question=question,
            history=history,
            indexes=indexes,
            top_k=top_k
        )

        answer = self.llm.generate(prompt=user_prompt, system_prompt=system_prompt)
        return answer, sources

    def stream(
        self,
        question: str,
        history: list[str] = None,
        indexes: list[str] = None,
        top_k: int = None
    ) -> tuple[Generator[str, None, None], list[dict]]:
        """Streaming RAG response with source attribution."""
        search_query, sources, system_prompt, user_prompt = self._prepare_context(
            question=question,
            history=history,
            indexes=indexes,
            top_k=top_k
        )

        stream_gen = self.llm.stream(prompt=user_prompt, system_prompt=system_prompt)
        return stream_gen, sources