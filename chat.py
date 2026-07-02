from config import LLM_MODEL

from utils.retriever import Retriever
from utils.prompt import PromptBuilder
from utils.llm import LLM

print("=" * 60)
print("Adorush AI Documentation Assistant")
print("=" * 60)

retriever = Retriever()
llm = LLM(LLM_MODEL)

while True:

    question = input("\nAsk a question (exit to quit): ")

    if question.lower() == "exit":
        break

    documents, metadata = retriever.retrieve(question)

    prompt = PromptBuilder.build(
        question,
        documents
    )

    answer = llm.generate(prompt)

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)

    print(answer)

    print("\nSources")

    for item in metadata:
        print(f"Page {item['page']}")