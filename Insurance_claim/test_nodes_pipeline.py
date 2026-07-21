import os
import sys

# Ensure local directories are visible to the interpreter path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all functional nodes built by Sai
from Insurance_claim.nodes.retrieve import retrieve_node
from Insurance_claim.nodes.grader import relevance_node
from Insurance_claim.nodes.adjudicate import adjudicate_node
from Insurance_claim.nodes.hallucination import hallucination_node
from Insurance_claim.nodes.escalate import escalation_node

def run_real_pdf_pipeline_test():
    print("=====================================================================")
    print("🔬 RUNNING PIPELINE INTEGRATION TEST UTILIZING PHYSICAL PDF DATA")
    print("=====================================================================\n")

    # Step 1: Initialize graph state with a realistic claim matching home_base_policy.pdf
    state = {
        "claim": "Filing a claim for building structure repair. My residential house suffered severe structural damage due to an earthquake storm peril.",
        "query": None,
        "documents": [],
        "retry_count": 0,
        "relevance": None,
        "decision": None,
        "confidence": 0.0,
        "hallucination": None,
        "audit_trail": ["Workflow initialized by user claim submission."]
    }

    print(f"📥 [Initial Claim State Submitted]:\n  \"{state['claim']}\"")

    # Step 2: Execute Retrieve Node (Queries local Chroma DB filled by Nayana's PDFs)
    state.update(retrieve_node(state))
    print(f"   -> Chunks now loaded in state: {len(state['documents'])}")

    # Step 3: Execute Relevance Grader Node (Grades actual PDF chunks via Anirudh's LLM chain)
    state.update(relevance_node(state))
    print(f"   -> State Relevance Result: {state['relevance']}")

    # Step 4: Conditional Adjudication Execution
    if state["relevance"] == "yes":
        # Pass real PDF texts extracted from Chroma down to the adjudicator node
        state.update(adjudicate_node(state))

        # Step 5: Execute Hallucination Guard over the generated response and source document text
        state.update(hallucination_node(state))

        # Step 6: Safety Check Gate (Triggers escalation node if confidence is too low or hallucinated)
        if state["confidence"] < 0.70 or state["hallucination"] == "no":
            print("\n⚠️ Safety guardrails triggered! Diverting to human agent node...")
            state.update(escalation_node(state))
    else:
        print("\n⚠️ Context was deemed irrelevant. In a full graph, this triggers query rewriting.")
        # Direct fallback for integration coverage assessment
        state.update(escalation_node(state))

    # Print out compiled pipeline output metrics
    print("\n=====================================================================")
    print("📊 FINAL CONSOLIDATED GRAPH STATE OUTPUT")
    print("=====================================================================")
    print(f"📢 Final Adjudication Decision : {state['decision']}")
    print(f"🎯 Calculated Confidence Score: {state['confidence']}")
    print(f"📝 System Final Output Answer  :\n{state['final_answer']}")
    print("\n📜 System Operational Audit Trail Logs:")
    for idx, log in enumerate(state['audit_trail']):
        print(f"  [{idx+1}] {log}")
    print("=====================================================================")

if __name__ == '__main__':
    run_real_pdf_pipeline_test()
