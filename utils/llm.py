import ollama


class LLM:

    def __init__(self, model):
        self.model = model

    # -------------------------------------
    # Normal Generation
    # -------------------------------------

    def generate(self, prompt):

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    # -------------------------------------
    # Streaming Generation
    # -------------------------------------

    def stream(self, prompt):

        stream = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        for chunk in stream:

            if "message" in chunk:

                content = chunk["message"].get("content", "")

                if content:
                    yield content