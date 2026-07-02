import ollama
from functools import lru_cache


@lru_cache(maxsize=1)
def get_embedding_model(model_name):
    print(f"Loading Embedder: {model_name}")
    return model_name


class Embedder:

    def __init__(self, model="nomic-embed-text"):
        self.model = get_embedding_model(model)

    def embed(self, text):

        response = ollama.embed(
            model=self.model,
            input=text
        )

        return response["embeddings"][0]