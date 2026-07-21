import os
import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

@st.cache_resource
def get_embedding_engine():
    print("🔄 [Retriever] Loading Hugging Face Embedding Engine into cache...")
    hf_token = os.environ.get("HF_TOKEN")
    if hasattr(st, "secrets") and "HF_TOKEN" in st.secrets:
        hf_token = st.secrets["HF_TOKEN"]
        
    model_kwargs = {}
    if hf_token:
        model_kwargs["token"] = hf_token

    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs=model_kwargs
    )

def fetch_context(query_text: str = None, query: str = None, top_k: int = 4):
    """
    Fetches context chunks from local Chroma DB.
    Supports both `query` and `query_text` keyword arguments.
    """
    # Resolve argument name variations
    search_query = query_text or query
    if not search_query:
        print("⚠️ [Retriever] Empty query passed to fetch_context.")
        return []

    if not os.path.exists(VECTOR_DB_DIR):
        print(f"⚠️ [Retriever] Directory missing at {VECTOR_DB_DIR}")
        return []

    embedding_engine = get_embedding_engine()
    vector_store = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embedding_engine
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    documents = retriever.invoke(search_query)
    print(f"📄 [Retriever] Found {len(documents)} context chunks for query: '{search_query[:40]}...'")
    return documents
