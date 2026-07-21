from typing import Dict, Any
from Insurance_claim.schemas.llm_chains import relevance_chain

def relevance_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates the quality of retrieved context blocks. If a single document
    chunk is scored as relevant, the context block passes validation.
    """
    print("\n[Node: Relevance Grader]")

    documents = state.get("documents", [])
    current_query = state.get("query") or state.get("claim")

    if not documents:
        print("  ⚠️ No documents found to grade.")
        return {
            "relevance": "no",
            "audit_trail": state.get("audit_trail", []) + ["Relevance check failed: No documents found."]
        }

    is_relevant = "no"
    rationales = []

    for idx, doc in enumerate(documents):
        res = relevance_chain.invoke({"query": current_query, "document": doc.page_content})
        print(f"  Chunk {idx+1} Relevance: {res.binary_score} | Rationale: {res.rationale}")
        if res.binary_score == "yes":
            is_relevant = "yes"
        rationales.append(f"Chunk {idx+1}: {res.binary_score} ({res.rationale})")

    log_entry = f"Relevance assessment concluded as [{is_relevant.upper()}]."
    updated_audit = state.get("audit_trail", []) + [log_entry]

    return {
        "relevance": is_relevant,
        "audit_trail": updated_audit
    }
