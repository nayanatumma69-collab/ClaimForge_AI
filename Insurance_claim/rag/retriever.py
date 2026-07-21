import os
import streamlit as st
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

# Cache embedding model in RAM and pass HF_TOKEN if available
@st.cache_resource
def get_embedding_engine():
    print("🔄 [Retriever] Loading Hugging Face Embedding Engine into cache...")
    
    # Retrieve HF Token from Streamlit secrets or OS environment
    hf_token = os.environ.get("HF_TOKEN")
    if hasattr(st, "secrets") and "HF_TOKEN" in st.secrets:
        hf_token = st.secrets["HF_TOKEN"]
        
    model_kwargs = {}
    if hf_token:
        model_kwargs["token"] = hf_token

    return HuggingFaceEmbeddings(
        model_name="openai/gpt-oss-120b",
        model_kwargs=model_kwargs
    )

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
