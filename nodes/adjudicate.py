from typing import Dict, Any
from Insurance_claim.schemas.llm_chains import adjudicate_chain

def adjudicate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes claim criteria against compiled context documents to
    generate a structured coverage decision, reason, and citations.
    """
    print("\n[Node: Claims Adjudicator]")

    claim = state.get("claim")
    documents = state.get("documents", [])

    # Compile text contents from all source documents
    context_block = ""
    for idx, doc in enumerate(documents):
        source = doc.metadata.get("source_file", "Unknown")
        category = doc.metadata.get("category", "Unknown")
        context_block += f"--- Document {idx+1} [Source: {source} | Category: {category}] ---\n"
        context_block += f"{doc.page_content}\n\n"

    print(f"  Evaluating claim against {len(documents)} context document source blocks...")

    # Run the adjudication chain
    res = adjudicate_chain.invoke({"claim": claim, "context": context_block})
    print(f"  ⚖️ Decision: {res.decision} | Confidence: {res.confidence}")

    log_entry = f"Adjudication completed with decision [{res.decision}] and confidence score {res.confidence}."
    updated_audit = state.get("audit_trail", []) + [log_entry]

    return {
        "decision": res.decision,
        "confidence": res.confidence,
        "final_answer": res.reason,
        "relevance": str(res.evidence_citations),  # Storing citations list as string temporarily for state parsing
        "audit_trail": updated_audit
    }
