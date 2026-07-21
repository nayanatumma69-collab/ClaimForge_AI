from typing import Dict, Any
from Insurance_claim.rag.retriever import fetch_context

def retrieve_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Queries the localized Chroma database using the current search query
    and saves the extracted document fragments into the state context.
    """
    print("\n[Node: Retrieve Context]")

    # Fallback to base claim if query isn't explicitly set yet by rewriter
    current_query = state.get("query") or state.get("claim")
    print(f"  🔍 Executing retrieval for query: '{current_query}'")

    # Pull top matching text blocks from your database
    retrieved_docs = fetch_context(query=current_query, top_k=3)

    # Format audit trail updates
    log_entry = f"Retrieved {len(retrieved_docs)} chunks from local vector store."
    updated_audit = state.get("audit_trail", []) + [log_entry]

    return {
        "documents": retrieved_docs,
        "audit_trail": updated_audit
    }
