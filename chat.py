from services.rag_service import RAGService
from services.knowledge_base_manager import KnowledgeBaseManager

print("=" * 60)
print("🤖 Adorush AI Documentation Assistant (CLI Mode)")
print("=" * 60)

rag_service = RAGService()
kb_mgr = KnowledgeBaseManager()
indexes = kb_mgr.list_indexes()

if not indexes:
    print("⚠️ No Knowledge Bases found! Please build one using app.py or build_index.py first.")
    exit(1)

print(f"Available Knowledge Bases: {', '.join(indexes)}")
history = []

while True:
    try:
        question = input("\nAsk a question (or 'exit' to quit): ").strip()
        if not question or question.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        print("\n🔍 Searching & Reranking...")
        answer, sources = rag_service.ask(
            question=question,
            history=history,
            indexes=indexes[:1]
        )

        print("\n" + "=" * 60)
        print("ANSWER")
        print("=" * 60)
        print(answer)

        print("\n📄 Sources Cited:")
        for s in sources[:3]:
            print(f"- Document: {s.get('source', s.get('index', 'Doc'))} (Page {s.get('page', 1)})")

        history.append(f"User: {question}")
        history.append(f"Assistant: {answer}")
        if len(history) > 6:
            history = history[-6:]

    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"❌ Error: {e}")