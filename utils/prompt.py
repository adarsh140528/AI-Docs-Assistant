class PromptBuilder:
    
    @staticmethod
    def build(question, documents, history=None):

        context = "\n\n".join(documents)

        conversation = ""

        if history:

            conversation = "\n".join(history)

        prompt = f"""
You are an expert documentation assistant.

Answer ONLY using the provided documentation.

If the answer is not present in the documentation, reply exactly:

"I couldn't find that information in the documentation."

========================
Conversation History
========================

{conversation}

========================
Documentation
========================

{context}

========================
Current Question
========================

{question}

Answer:
"""

        return prompt