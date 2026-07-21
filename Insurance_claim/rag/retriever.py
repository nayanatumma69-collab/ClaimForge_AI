import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Calculate absolute path relative to this script file location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

print(f"🔍 [Retriever] Querying Vector Database at: {VECTOR_DB_DIR}")

# Load the local HuggingFace embedding engine
embedding_engine = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def fetch_context(query_text: str, top_k: int = 4):
    """Fetches the top_k most relevant PDF context chunks from local Chroma DB."""
    if not os.path.exists(VECTOR_DB_DIR):
        print(f"⚠️ [Retriever] Directory missing at {VECTOR_DB_DIR}")
        return []

    vector_store = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embedding_engine
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    documents = retriever.invoke(query_text)
    print(f"📄 [Retriever] Found {len(documents)} context chunks for query: '{query_text[:40]}...'")
    return documents
