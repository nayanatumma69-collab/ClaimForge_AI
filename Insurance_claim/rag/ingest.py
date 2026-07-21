import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

def run_ingestion():
    print(f"📥 [Ingest] Reading PDFs from: {DATA_DIR}")
    print(f"💾 [Ingest] Target Vector DB path: {VECTOR_DB_DIR}")

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        print("⚠️ Data directory created.")

    loader = PyPDFDirectoryLoader(DATA_DIR)
    docs = loader.load()

    if not docs:
        print("⚠️ No PDF files found in data directory!")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    print(f"✂️ Split {len(docs)} documents into {len(chunks)} chunks.")

    # Using lightweight MiniLM embedding model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    print("✅ Ingestion complete! Vector store successfully generated.")

if __name__ == "__main__":
    run_ingestion()
