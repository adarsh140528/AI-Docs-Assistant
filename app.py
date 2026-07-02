import os
import streamlit as st
from rag import ask, stream, reload
from services.index_service import IndexService
import json

# -------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# -------------------------------------------------

st.set_page_config(
    page_title="Adorush AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# LOAD CSS
# -------------------------------------------------

def load_css():
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "stats" not in st.session_state:
    st.session_state.stats = {
        "documents": 0,
        "pages": 0,
        "chunks": 0,
        "index": None
    }

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

with st.sidebar:

    st.title("🤖 Adorush AI")
    st.caption("Enterprise Documentation Platform")
    st.divider()

    # ---------------------------------------------
    # PDF Upload
    # ---------------------------------------------

    st.subheader("📂 Upload Documentation")

    uploaded_file = st.file_uploader(
        "Choose PDF",
        type=["pdf"]
    )

    if uploaded_file:

        os.makedirs("uploads", exist_ok=True)

        pdf_path = os.path.join(
            "uploads",
            uploaded_file.name
        )

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("✅ PDF Uploaded")

        if st.button(
            "🚀 Build Knowledge Base",
            use_container_width=True
        ):

            with st.spinner("Building Knowledge Base..."):

                stats = IndexService().build(
                    pdf_path=pdf_path,
                    pdf_filename=uploaded_file.name
                )

            reload()

            st.session_state.stats = {
                "documents": 1,
                "pages": stats["pages"],
                "chunks": stats["chunks"],
                "index": stats["index"]
            }

            st.success("✅ Knowledge Base Created!")
            st.success(f"📚 {stats['index']}")

    st.divider()

    # ---------------------------------------------
    # KNOWLEDGE BASE
    # ---------------------------------------------

    st.subheader("📊 Knowledge Base")

    from services.knowledge_base_manager import (
        KnowledgeBaseManager
    )

    kb = KnowledgeBaseManager()

    available_indexes = kb.list_indexes()

    selected_indexes = st.multiselect(
        "📚 Search Knowledge Bases",
        options=available_indexes,
        default=[]
    )

    if not selected_indexes:
        st.info("Please select one or more Knowledge Bases.")

    st.metric("Documents", st.session_state.stats["documents"])
    st.metric("Pages", st.session_state.stats["pages"])
    st.metric("Chunks", st.session_state.stats["chunks"])

    st.write("**Active Knowledge Base**")
    st.code(st.session_state.stats["index"] or "None")

    st.divider()

    # ---------------------------------------------
    # MODELS
    # ---------------------------------------------

    st.subheader("⚙️ Models")

    st.write("**LLM**")
    st.code("llama3.2:3b")

    st.write("**Embedding Model**")
    st.code("nomic-embed-text")

    st.divider()

    if st.button(
        "🗑 Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("🤖 Adorush AI")

st.subheader("Enterprise Documentation Assistant")

st.caption(
    "Powered by Llama 3.2 • Ollama • ChromaDB • Semantic Search"
)



st.divider()

# -------------------------------------------------
# CHAT HISTORY
# -------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------------------------
# CHAT INPUT
# -------------------------------------------------
# -------------------------------------------------
# CHAT INPUT
# -------------------------------------------------

question = st.chat_input(
    "Ask anything about the documentation..."
)

if question:

    # -----------------------------
    # Save User Message
    # -----------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # -----------------------------
    # Build Conversation History
    # -----------------------------

    history = []

    for msg in st.session_state.messages[:-1][-6:]:

        role = (
            "User"
            if msg["role"] == "user"
            else "Assistant"
        )

        history.append(
            f"{role}: {msg['content']}"
        )

    # -----------------------------
    # Ask RAG
    # -----------------------------

    if not selected_indexes:

        st.warning(
            "⚠️ Please select at least one Knowledge Base."
        )

        st.stop()

    with st.spinner("🔍 Searching documentation..."):

        stream_generator, sources = stream(
            question,
            history,
            selected_indexes
        )

    # -----------------------------
    # Assistant Response
    # -----------------------------

    with st.chat_message("assistant"):

        answer = st.write_stream(
            stream_generator
        )

        st.divider()

        st.markdown("### 📄 Sources")

        seen_sources = set()
        display_sources = []

        for source in sources:

            key = (
                source.get("index", "Current KB"),
                source["page"]
            )

            if key not in seen_sources:

                seen_sources.add(key)
                display_sources.append(source)

        for source in display_sources[:3]:

            kb_name = source.get(
                "index",
                "Current KB"
            )

            with st.expander(
                f"📚 {kb_name} | 📄 Page {source['page']}"
            ):

                page = str(source["page"])
                index = source.get("index")

                # Single KB fallback
                if index is None:

                    from services.knowledge_base_manager import (
                        KnowledgeBaseManager
                    )

                    kb = KnowledgeBaseManager()

                    index = kb.get_current()

                pages_file = os.path.join(
                    "indexes",
                    index,
                    "pages.json"
                )

                preview = source["content"]

                if os.path.exists(pages_file):

                    try:

                        with open(
                            pages_file,
                            "r",
                            encoding="utf-8"
                        ) as f:

                            pages = json.load(f)

                        preview = pages.get(
                            page,
                            preview
                        )

                        if len(preview) > 1000:

                            preview = (
                                preview[:1000]
                                + "\n\n... (Page truncated)"
                            )

                    except Exception:
                        pass

                st.markdown(preview)


    # -----------------------------
    # Save Assistant Message
    # -----------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.divider()

st.caption(
    "Built with ❤️ using Python • Ollama • ChromaDB • Streamlit"
)