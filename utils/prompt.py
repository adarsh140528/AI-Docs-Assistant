class PromptBuilder:
    """
    Constructs grounded RAG prompts with source annotations
    and provides conversational query condensation templates.
    """

    @staticmethod
    def build_rag_prompt(
        question: str,
        documents: list[str],
        sources: list[dict] = None,
        history: list[str] = None
    ) -> tuple[str, str]:
        """
        Builds (system_prompt, user_prompt) with formatted context.
        """
        system_prompt = (
            "You are an expert AI documentation assistant. "
            "Your task is to provide clear, accurate, and structured answers based ONLY on the provided context.\n"
            "Guidelines:\n"
            "1. Rely strictly on the provided documentation context.\n"
            "2. Whenever possible, cite the document name and page number from which the information comes.\n"
            "3. Use clean markdown (headings, bullet points, code blocks) to make your response easy to read.\n"
            "4. If the context does not contain enough information to answer the question, clearly state: "
            "'I couldn't find sufficient information in the provided documentation to answer that question.'"
        )

        formatted_contexts = []
        for i, doc in enumerate(documents):
            source_info = "Document"
            page_info = "?"
            if sources and i < len(sources):
                source_info = sources[i].get("source", sources[i].get("index", "Document"))
                page_info = sources[i].get("page", 1)
            formatted_contexts.append(
                f"[Source: {source_info} | Page: {page_info}]\n{doc}"
            )

        context_block = "\n\n---\n\n".join(formatted_contexts) if formatted_contexts else "No context available."

        history_block = ""
        if history:
            history_text = "\n".join(history)
            history_block = f"### Recent Conversation History:\n{history_text}\n\n"

        user_prompt = f"""{history_block}### Context Documentation:
{context_block}

### User Question:
{question}

### Answer:"""

        return system_prompt, user_prompt

    @staticmethod
    def build(question: str, documents: list[str], history: list[str] = None, sources: list[dict] = None) -> str:
        """Backward-compatible single-prompt builder."""
        system_prompt, user_prompt = PromptBuilder.build_rag_prompt(
            question=question,
            documents=documents,
            sources=sources,
            history=history
        )
        return f"{system_prompt}\n\n{user_prompt}"

    @staticmethod
    def build_query_condensation_prompt(question: str, history: list[str]) -> str:
        """
        Generates a prompt to rewrite a conversational follow-up question
        into a standalone search query.
        """
        history_str = "\n".join(history[-4:])
        return f"""Given the following conversation history and a follow-up question, rephrase the follow-up question into a standalone, self-contained search query suitable for semantic vector and keyword search. Do NOT answer the question, only output the standalone search query.

Conversation History:
{history_str}

Follow-up Question: {question}

Standalone Search Query:"""