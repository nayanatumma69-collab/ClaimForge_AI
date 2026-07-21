from typing import Dict, Any
from Insurance_claim.schemas.llm_chains import rewrite_chain

def rewrite_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the unoptimized query and re-engineers it using the LLM
    to extract optimal keyword vectors for subsequent retrieval.
    """
    print("\n[Node: Query Rewriter]")

    current_query = state.get("query") or state.get("claim")
    print(f"  Refining unoptimized search term: '{current_query}'")

    # Invoke Anirudh's rewrite engine
    res = rewrite_chain.invoke({"query": current_query})
    print(f"  🚀 Re-engineered Query: '{res.optimized_query}'")

    # Increment tracking loops to prevent infinite lookups
    current_retry = state.get("retry_count", 0) + 1

    log_entry = f"Query rewritten from '{current_query}' to '{res.optimized_query}' (Attempt {current_retry})."
    updated_audit = state.get("audit_trail", []) + [log_entry]

    return {
        "query": res.optimized_query,
        "retry_count": current_retry,
        "audit_trail": updated_audit
    }
