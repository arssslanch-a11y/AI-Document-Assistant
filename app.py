import os
import requests

import streamlit as st
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from llm.answer_generator import generate_answer


# =========================================================
# CONFIGURATION
# =========================================================

FAISS_FOLDER = "faiss_index"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🤖 AI Document Assistant")

st.write(
    "Upload one or more PDF documents and ask questions "
    "from their content."
)


# =========================================================
# EMBEDDING MODEL
# =========================================================

@st.cache_resource
def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# =========================================================
# LOAD EXISTING FAISS DATABASE
# =========================================================

if os.path.exists(FAISS_FOLDER):

    if "vector_db" not in st.session_state:

        try:

            embeddings = get_embeddings()

            vector_db = FAISS.load_local(
                FAISS_FOLDER,
                embeddings,
                allow_dangerous_deserialization=True
            )

            st.session_state["vector_db"] = vector_db

        except Exception:

            pass


# =========================================================
# PDF UPLOAD
# =========================================================

st.subheader("📂 Upload Documents")

uploaded_files = st.file_uploader(
    "Choose one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# =========================================================
# SHOW SELECTED FILES
# =========================================================

if uploaded_files:

    st.subheader("📄 Selected Documents")

    for file in uploaded_files:

        st.write(f"✓ {file.name}")


# =========================================================
# PROCESS DOCUMENTS
# =========================================================

if uploaded_files:

    if st.button(
        "🚀 Process Documents",
        type="primary"
    ):

        st.subheader(
            "📖 Processing Documents..."
        )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        all_chunks = []
        all_metadata = []

        # -------------------------------------------------
        # READ PDF FILES
        # -------------------------------------------------

        for uploaded_file in uploaded_files:

            try:

                reader = PdfReader(
                    uploaded_file
                )

                for page_number, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    text = page.extract_text()

                    if not text:
                        continue

                    chunks = text_splitter.split_text(
                        text
                    )

                    for chunk in chunks:

                        if chunk.strip():

                            all_chunks.append(
                                chunk
                            )

                            all_metadata.append(
                                {
                                    "source": uploaded_file.name,
                                    "page": page_number
                                }
                            )

            except Exception as e:

                st.error(
                    f"❌ Could not process {uploaded_file.name}: {e}"
                )

                st.stop()

        # -------------------------------------------------
        # CHECK DATA
        # -------------------------------------------------

        if not all_chunks:

            st.error(
                "❌ No readable text was found in the PDF files."
            )

            st.stop()

        st.success(
            f"✅ Created {len(all_chunks)} text chunks."
        )

        # -------------------------------------------------
        # CREATE EMBEDDINGS
        # -------------------------------------------------

        st.info(
            "🧠 Creating embeddings..."
        )

        embeddings = get_embeddings()

        # -------------------------------------------------
        # CREATE FAISS DATABASE
        # -------------------------------------------------

        st.info(
            "🗂️ Creating FAISS vector database..."
        )

        vector_db = FAISS.from_texts(
            texts=all_chunks,
            embedding=embeddings,
            metadatas=all_metadata
        )

        # -------------------------------------------------
        # SAVE FAISS
        # -------------------------------------------------

        vector_db.save_local(
            FAISS_FOLDER
        )

        st.session_state["vector_db"] = vector_db

        st.success(
            "🎉 FAISS vector database created successfully!"
        )

        st.write(
            f"📦 **Total chunks:** {len(all_chunks)}"
        )

        st.success(
            "💾 FAISS database saved locally."
        )


# =========================================================
# ASK QUESTION
# =========================================================

if "vector_db" in st.session_state:

    st.divider()

    st.subheader(
        "💬 Ask a Question"
    )

    question = st.text_area(
        "Ask something about your documents:",
        placeholder=(
            "Example: What is the main purpose of this document?"
        )
    )

    if st.button(
        "🤖 Ask",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "⚠️ Please enter a question."
            )

        else:

            # -------------------------------------------------
            # RETRIEVE RELEVANT CHUNKS
            # -------------------------------------------------

            with st.spinner(
                "🔎 Searching relevant information..."
            ):

                try:

                    results = (
                        st.session_state["vector_db"]
                        .similarity_search(
                            question,
                            k=4
                        )
                    )

                except Exception as e:

                    st.error(
                        f"❌ Search failed: {e}"
                    )

                    st.stop()


            if not results:

                st.warning(
                    "❌ No relevant information was found."
                )

            else:

                st.success(
                    f"✅ Found {len(results)} relevant sections."
                )

                # -------------------------------------------------
                # BUILD CONTEXT HERE
                # -------------------------------------------------

                context_parts = []
                sources = []

                for result in results:

                    text = result.page_content

                    source = result.metadata.get(
                        "source",
                        "Unknown"
                    )

                    page = result.metadata.get(
                        "page",
                        "Unknown"
                    )

                    context_parts.append(
                        f"""
SOURCE: {source}
PAGE: {page}

{text}
"""
                    )

                    sources.append(
                        {
                            "source": source,
                            "page": page
                        }
                    )

                # THIS WAS THE MISSING PART
                context = "\n\n".join(
                    context_parts
                )

                # -------------------------------------------------
                # GENERATE AI ANSWER
                # -------------------------------------------------

                with st.spinner(
                    "🤖 AI is preparing your answer..."
                ):

                    try:

                        answer = generate_answer(
                            question,
                            context
                        )

                    except requests.exceptions.ConnectionError:

                        st.error(
                            "❌ Ollama is not running. "
                            "Please start Ollama and try again."
                        )

                        st.stop()

                    except requests.exceptions.Timeout:

                        st.error(
                            "⏳ AI took too long to respond. "
                            "Please try again."
                        )

                        st.stop()

                    except Exception as e:

                        st.error(
                            f"❌ AI answer generation failed: {e}"
                        )

                        st.stop()

                # -------------------------------------------------
                # DISPLAY ANSWER
                # -------------------------------------------------

                st.subheader(
                    "🤖 Answer"
                )

                if answer:

                    st.write(answer)

                else:

                    st.warning(
                        "⚠️ The AI could not generate an answer."
                    )

                # -------------------------------------------------
                # DISPLAY SOURCES
                # -------------------------------------------------

                st.subheader(
                    "📖 Sources"
                )

                unique_sources = set()

                for source in sources:

                    source_key = (
                        source["source"],
                        source["page"]
                    )

                    if source_key not in unique_sources:

                        unique_sources.add(
                            source_key
                        )

                        st.write(
                            f"📄 **{source['source']}** — "
                            f"Page **{source['page']}**"
                        )