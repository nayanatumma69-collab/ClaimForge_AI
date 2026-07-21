import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_and_split_insurance_docs() -> List[Document]:
    """
    Scans the data subdirectories, extracts raw text from PDF binaries,
    splits them using an overlap strategy, and injects structural metadata.
    """
    base_data_dir = "Insurance_claim/data"
    doc_categories = {
        "policy": os.path.join(base_data_dir, "policies"),
        "endorsement": os.path.join(base_data_dir, "endorsements"),
        "regulation": os.path.join(base_data_dir, "regulations")
    }

    all_chunks = []

    # Configure the text splitter to keep sections intact
    # 450 characters max per chunk with an overlap window of 50 characters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=450,
        chunk_overlap=50,
        length_function=len,
        add_start_index=True
    )

    print("🚀 Initializing insurance document chunking engine...")

    for category, dir_path in doc_categories.items():
        if not os.path.exists(dir_path):
            continue

        for file_name in os.listdir(dir_path):
            if file_name.endswith(".pdf"):
                file_path = os.path.join(dir_path, file_name)
                print(f"  Parsing document category [{category.upper()}]: {file_name}")

                try:
                    loader = PyPDFLoader(file_path)
                    raw_pages = loader.load()

                    # Split pages into granular text chunks
                    chunks = text_splitter.split_documents(raw_pages)

                    # Core task: Inject tracking metadata tags for the team's Evidence Citations
                    for chunk in chunks:
                        chunk.metadata["category"] = category
                        chunk.metadata["source_file"] = file_name
                        all_chunks.append(chunk)

                except Exception as e:
                    print(f"  ❌ Failed to parse document {file_name}: {str(e)}")

    print(f"\n✅ Processing finalized! Total chunks generated: {len(all_chunks)}")
    return all_chunks

if __name__ == "__main__":
    # Internal execution test check
    load_and_split_insurance_docs()
