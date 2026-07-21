from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class RelevanceGrade(BaseModel):
    """Structured rating to check if retrieved documents match the claim context."""
    binary_score: Literal["yes", "no"] = Field(
        description="Is the document explicitly relevant to the user's insurance claim? 'yes' or 'no'"
    )
    rationale: str = Field(
        description="A brief sentence explaining why the document is or isn't relevant."
    )

class RewriteOutput(BaseModel):
    """Structured instruction for rewriting unoptimized search queries."""
    optimized_query: str = Field(
        description="The newly engineered, keyword-focused search query optimized for vector database lookup."
    )

class DecisionOutput(BaseModel):
    """The central adjudication logic schema for evaluating insurance coverage."""
    decision: Literal["Covered", "Not Covered", "Escalate"] = Field(
        description="Final claim adjustment assessment based exclusively on policy terms."
    )
    confidence: float = Field(
        description="Confidence score decimal metric strictly between 0.0 and 1.0 representing mathematical decision certainty."
    )
    reason: str = Field(
        description="Detailed contextual breakdown justifying the final coverage determination."
    )
    evidence_citations: List[str] = Field(
        description="List of raw strings identifying specific policies, endorsements, or clauses explicitly utilized."
    )

class HallucinationGrade(BaseModel):
    """Validation schema to verify the LLM's claim decision matches the context facts perfectly."""
    is_grounded: Literal["yes", "no"] = Field(
        description="Does the decision text strictly originate from the provided documents without hallucinated details? 'yes' or 'no'"
    )
    rationale: str = Field(
        description="Detailed logical proof mapping the generation elements back to source facts."
    )

class HumanEscalation(BaseModel):
    """Routing schema used when an edge case requires human supervisor intervention."""
    escalation_required: bool = Field(
        description="Flag indicating if the system must yield execution authority to a human claims specialist."
    )
    routing_reason: str = Field(
        description="Explicit breakdown of failure constraints (e.g., conflicting clauses, low confidence, text hallucination)."
    )
