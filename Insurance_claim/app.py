import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set page config FIRST before any heavy modules load
st.set_page_config(
    page_title="ClaimForge AI — Adjudication Hub",
    page_icon="⚖️",
    layout="wide"
)

# Cache ingestion so it only runs ONCE per container lifecycle
@st.cache_resource
def initialize_vector_store():
    VECTOR_DB_PATH = "Insurance_claim/vector_db"
    if not os.path.exists(VECTOR_DB_PATH) or len(os.listdir(VECTOR_DB_PATH)) == 0:
        try:
            import importlib
            ingest_module = importlib.import_module("Insurance_claim.rag.ingest")
            if hasattr(ingest_module, "run_ingestion"):
                ingest_module.run_ingestion()
            else:
                exec(open("Insurance_claim/rag/ingest.py").read())
            return "SUCCESS"
        except Exception as e:
            return f"ERROR: {str(e)}"
    return "EXISTS"

# Run store initialization status check
store_status = initialize_vector_store()
if "ERROR" in store_status:
    st.error(f"❌ Document Ingestion Error: {store_status}")

# Import compiled LangGraph engine
from Insurance_claim.graph import app_engine

st.title("⚖️ ClaimForge AI — Agentic Adjudication Portal")
st.markdown("---")

col_input, col_results = st.columns([1, 1.2])

with col_input:
    st.subheader("📋 Claim Submission Panel")
    user_claim = st.text_area(
        label="Enter Claim Statement Description:",
        placeholder="e.g., Filing a claim for home structure repairs. My house suffered severe structural damage due to an earthquake storm peril.",
        height=150
    )
    analyze_submitted = st.button("🚀 Analyze & Adjudicate Claim", use_container_width=True)

with col_results:
    st.subheader("📊 Operational Adjudication Metrics")
    
    if analyze_submitted:
        if not user_claim.strip():
            st.error("⚠️ Please enter a valid text claim description before analyzing.")
        else:
            with st.spinner("Processing claims workflow loops across backend nodes..."):
                try:
                    inputs = {
                        "claim": user_claim,
                        "query": None,
                        "documents": [],
                        "retry_count": 0,
                        "relevance": "no",
                        "decision": "Pending",
                        "confidence": 0.0,
                        "final_answer": "",
                        "audit_trail": ["Workflow initialized via dashboard panel submission."]
                    }
                    
                    final_output_state = app_engine.invoke(inputs)
                    
                    decision = final_output_state.get("decision", "Escalate")
                    confidence = final_output_state.get("confidence", 0.0)
                    explanation = final_output_state.get("final_answer", "N/A")
                    logs = final_output_state.get("audit_trail", [])
                    
                    if decision == "Covered":
                        st.success(f"### 🎉 Decision Status: {decision}")
                    elif decision == "Not Covered":
                        st.error(f"### ❌ Decision Status: {decision}")
                    else:
                        st.warning(f"### ⚠️ Decision Status: {decision} (Manual Hand-off)")
                        
                    st.metric(label="🎯 System Certainty Score", value=f"{int(confidence * 100)}%")
                    st.progress(float(confidence))
                    
                    st.markdown("#### 📝 Determination Summary & Reason")
                    st.info(explanation)
                    
                    with st.expander("📜 System Engine Audit Trail Logs"):
                        for idx, step in enumerate(logs):
                            st.write(f"**[{idx+1}]** {step}")
                            
                except Exception as e:
                    st.error(f"❌ Structural Processing Pipeline Error: {str(e)}")
    else:
        st.caption("Awaiting claim submission profile data input to run analysis.")
