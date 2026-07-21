from typing import Dict, Any
from Insurance_claim.schemas.llm_chains import hallucination_chain

def hallucination_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs a factual audit checking if the reasoning matches the facts.
    """
    print("\n[Node: Hallucination Quality Guard]")

    documents = state.get("documents", [])
    decision = state.get("decision")
    final_answer = state.get("final_answer")

    # Recompile documents for factual source auditing
    context_block = "\n".join([doc.page_content for doc in documents])
    decision_details = f"Decision: {decision}\nReasoning: {final_answer}"

    # Run hallucination verification
    res = hallucination_chain.invoke({"context": context_block, "decision_details": decision_details})
    print(f"  Grounded Verification: {res.is_grounded} | Rationale: {res.rationale}")

    log_entry = f"Hallucination check passed: [{res.is_grounded}]. Rationale: {res.rationale}"
    updated_audit = state.get("audit_trail", []) + [log_entry]

    return {
        "hallucination": res.is_grounded,
        "audit_trail": updated_audit
    }
