import os
import streamlit as st
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

# Cache embedding model in RAM across user re-runs to stay under 1GB memory limit
@st.cache_resource
def get_embedding_engine():
    print("🔄 [Retriever] Loading Hugging Face Embedding Engine into cache...")
    return HuggingFaceEmbeddings(model_name="openai/gpt-oss-120b")

def fetch_context(query_text: str, top_k: int = 4):
    """Fetches context chunks from local Chroma DB."""
    if not os.path.exists(VECTOR_DB_DIR):
        print(f"⚠️ [Retriever] Directory missing at {VECTOR_DB_DIR}")
        return []

    embedding_engine = get_embedding_engine()

    vector_store = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embedding_engine
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    documents = retriever.invoke(query_text)
    print(f"📄 [Retriever] Found {len(documents)} context chunks.")
    return documents
