from typing import Dict, Any
from Insurance_claim.schemas.llm_chains import escalate_chain

def escalation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gracefully intercepts problematic claims (low confidence, hallucinations,
    or logic conflicts) and constructs a structured handoff brief for human review.
    """
    print("\n[Node: Human Escalation Hand-off]")

    claim = state.get("claim")
    confidence = state.get("confidence", 0.0)
    hallucination = state.get("hallucination", "yes")

    # Determine the structural trigger reason
    if hallucination == "no":
        trigger = "Adjudication reasoning failed factual grounding validation checks (Hallucination Detected)."
    elif confidence < 0.70:
        trigger = f"System certainty score ({confidence}) fell below the mandatory 0.70 threshold."
    else:
        trigger = "Claim flagged for manual intervention due to internal workflow routing rules."

    print(f"  Escalating claim. Reason: {trigger}")

    # Invoke the escalation briefer chain
    res = escalate_chain.invoke({"claim": claim, "routing_reason": trigger})

    log_entry = f"Claim successfully rerouted to a human specialist. Handover Brief Generated."
    updated_audit = state.get("audit_trail", []) + [log_entry]

    return {
        "decision": "Escalate",
        "final_answer": res.routing_reason,  # The handoff brief becomes the final displayed answer
        "audit_trail": updated_audit
    }
