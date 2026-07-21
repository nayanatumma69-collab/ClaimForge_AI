import os
from typing import List
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from Insurance_claim.rag.ingest import load_and_split_insurance_docs

# 1. Define configuration constants
DB_DIR = "Insurance_claim/vector_db"

def get_vector_store() -> Chroma:
    """
    Initializes or loads the Chroma vector database.
    If the database is empty, it runs the ingestion script to populate it.
    """
    # Using a reliable, lightweight open-source embedding model that runs perfectly for free in Colab
    print("Loading HuggingFace Embedding Model ('all-MiniLM-L6-v2')...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # If database files don't exist yet, build them
    if not os.listdir(DB_DIR):
        print("Vector database is empty. Running data ingestion...")
        chunks = load_and_split_insurance_docs()

        print(f"Indexing {len(chunks)} chunks into Chroma DB...")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=DB_DIR
        )
        print("✅ Vector database successfully created and saved!")
    else:
        print("💾 Found existing vector database. Loading from disk...")
        vector_store = Chroma(
            persist_directory=DB_DIR,
            embedding_function=embeddings
        )

    return vector_store

def fetch_context(query: str, top_k: int = 3) -> List[Document]:
    """
    Exposes a clean interface for Team Member 3 (Sai) to call from LangGraph nodes.
    Returns the top matching context blocks for a given claim search string.
    """
    try:
        vector_store = get_vector_store()
        # Perform similarity search
        results = vector_store.similarity_search(query, k=top_k)
        return results
    except Exception as e:
        print(f"❌ Error during context retrieval: {str(e)}")
        return []

# Standalone manual test block
if __name__ == "__main__":
    print("--- Running Retriever Test ---")
    sample_query = "Claim for medical hospitalisation due to accidental injury"
    matched_docs = fetch_context(sample_query, top_k=2)

    print(f"\nResults for query: '{sample_query}'")
    for i, doc in enumerate(matched_docs):
        print(f"\n[Match {i+1}] Source File: {doc.metadata.get('source_file')} | Category: {doc.metadata.get('category')}")
        print(f"Content:\n{doc.page_content}")
