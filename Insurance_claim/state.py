from typing import TypedDict, List, Optional, Any
from langchain_core.documents import Document

class InsuranceState(TypedDict):
    """
    Global structural state tracker for the LangGraph workflow network.
    Houses context keys generated or consumed across all functional nodes.
    """
    claim: str                  # The raw text input submitted by the user
    query: Optional[str]        # The optimized text string handled by the query rewriter
    documents: List[Document]   # Compiled context text fragments pulled from local RAG or Tavily
    retry_count: int            # Dynamic iteration loop count tracker to block infinite query loops
    relevance: str              # Binary flag indicator ('yes' / 'no') populated by the grader
    decision: str               # The operational adjustment decision ('Covered', 'Not Covered', 'Escalate')
    confidence: float           # The calculated certainty score decimal value between 0.0 and 1.0
    final_answer: str           # The textual reasoning response or manual handover brief details
    audit_trail: List[str]      # Appending history logs documenting exact pipeline node transitions
