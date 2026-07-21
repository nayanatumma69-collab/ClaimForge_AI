from langgraph.graph import StateGraph, START, END
from typing import Literal

# Import the structural state shape built in Step 1
from Insurance_claim.state import InsuranceState

# Import all processing node components built by Sai
from Insurance_claim.nodes.retrieve import retrieve_node
from Insurance_claim.nodes.grader import relevance_node
from Insurance_claim.nodes.rewrite import rewrite_node
from Insurance_claim.nodes.websearch import web_search_node
from Insurance_claim.nodes.adjudicate import adjudicate_node
from Insurance_claim.nodes.hallucination import hallucination_node
from Insurance_claim.nodes.escalate import escalation_node

# ---------------------------------------------------------------------
# CONDITIONAL ROUTING ROUTERS (THE CONTROL GATES)
# ---------------------------------------------------------------------

def route_after_relevance(state: InsuranceState) -> Literal["adjudicate", "rewrite"]:
    """Routes the claim based on context relevance."""
    if state.get("relevance") == "yes":
        return "adjudicate"
    return "rewrite"

def route_after_rewrite(state: InsuranceState) -> Literal["retrieve", "websearch"]:
    """Controls the recovery loop threshold to prevent infinite processing maps."""
    if state.get("retry_count", 0) <= 2:
        return "retrieve"
    return "websearch"

def route_after_quality_check(state: InsuranceState) -> Literal["escalate", "end"]:
    """Enforces strict security guardrails against hallucinations and low confidence."""
    confidence = state.get("confidence", 0.0)
    hallucination = state.get("hallucination", "yes")

    if confidence < 0.70 or hallucination == "no":
        return "escalate"
    return "end"

# ---------------------------------------------------------------------
# GRAPH ASSEMBLY AND COMPILATION
# ---------------------------------------------------------------------

# Initialize the StateGraph using our custom defined structural state memory
workflow = StateGraph(InsuranceState)

# Register all operational node execution points into the graph network
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grader", relevance_node)
workflow.add_node("rewrite", rewrite_node)
workflow.add_node("websearch", web_search_node)
workflow.add_node("adjudicate", adjudicate_node)
workflow.add_node("hallucination", hallucination_node)
workflow.add_node("escalate", escalation_node)

# Construct static execution links
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "grader")

# Inject the Relevance routing decision checkpoint
workflow.add_conditional_edges(
    "grader",
    route_after_relevance,
    {
        "adjudicate": "adjudicate",
        "rewrite": "rewrite"
    }
)

# Inject the Query Retry loop control checkpoint
workflow.add_conditional_edges(
    "rewrite",
    route_after_rewrite,
    {
        "retrieve": "retrieve",
        "websearch": "websearch"
    }
)

# Route direct web search results straight into the adjudication node
workflow.add_edge("websearch", "adjudicate")

# Route adjudication decisions through the hallucination verification layer
workflow.add_edge("adjudicate", "hallucination")

# Inject the final Safety Assessment guardrail routing checkpoint
workflow.add_conditional_edges(
    "hallucination",
    route_after_quality_check,
    {
        "escalate": "escalate",
        "end": END
    }
)

# Route manual handover briefs cleanly to final termination
workflow.add_edge("escalate", END)

# Compile the graph configuration layout into a runnable application engine
app_engine = workflow.compile()
print("🎯 LangGraph workflow network graph successfully compiled and ready for deployment!")
