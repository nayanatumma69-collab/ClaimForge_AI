import os
import sys
import streamlit as st

# Ensure local directories are visible to the interpreter path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------------------------------------------------------------------
# SELF-HEALING VECTOR STORE CHECK (FOR STREAMLIT CLOUD)
# ---------------------------------------------------------------------
VECTOR_DB_PATH = "Insurance_claim/vector_db"

if not os.path.exists(VECTOR_DB_PATH) or len(os.listdir(VECTOR_DB_PATH)) == 0:
    st.warning("⚠️ Vector store index missing. Running initial document ingestion for PDF files...")
    try:
        import importlib
        ingest_module = importlib.import_module("Insurance_claim.rag.ingest")
        
        # Flexibly locate and run the main ingestion function
        if hasattr(ingest_module, "run_ingestion"):
            ingest_module.run_ingestion()
        elif hasattr(ingest_module, "ingest_documents"):
            ingest_module.ingest_documents()
        elif hasattr(ingest_module, "main"):
            ingest_module.main()
        else:
            # Fallback: execute as a script if no standard function signature is matched
            exec(open("Insurance_claim/rag/ingest.py").read())
            
        st.success("✅ PDF Policy Documents successfully embedded and indexed!")
    except Exception as e:
        st.error(f"❌ Document Ingestion Error: {str(e)}")

# Import the compiled LangGraph engine
from Insurance_claim.graph import app_engine

# Set up clean professional page config
st.set_page_config(
    page_title="ClaimForge AI — Adjudication Hub",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ ClaimForge AI — Agentic Adjudication Portal")
st.markdown("---")

# Main Input Form Column Layout
col_input, col_results = st.columns([1, 1.2])

with col_input:
    st.subheader("📋 Claim Submission Panel")
    
    # Text input for the claim request
    user_claim = st.text_area(
        label="Enter Claim Statement Description:",
        placeholder="e.g., Filing a claim for home structure repairs. My house suffered severe structural damage due to an earthquake storm peril.",
        height=150
    )
    
    # Interactive action invocation button
    analyze_submitted = st.button("🚀 Analyze & Adjudicate Claim", use_container_width=True)

with col_results:
    st.subheader("📊 Operational Adjudication Metrics")
    
    if analyze_submitted:
        if not user_claim.strip():
            st.error("⚠️ Please enter a valid text claim description before analyzing.")
        else:
            with st.spinner("Processing claims workflow loops across backend nodes..."):
                try:
                    # Formulate initial LangGraph State payload dict
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
                    
                    # Run the LangGraph execution graph end-to-end
                    final_output_state = app_engine.invoke(inputs)
                    
                    # Extract decision parameters
                    decision = final_output_state.get("decision", "Escalate")
                    confidence = final_output_state.get("confidence", 0.0)
                    explanation = final_output_state.get("final_answer", "N/A")
                    logs = final_output_state.get("audit_trail", [])
                    
                    # 1. Decision Status Badges
                    if decision == "Covered":
                        st.success(f"### 🎉 Decision Status: {decision}")
                    elif decision == "Not Covered":
                        st.error(f"### ❌ Decision Status: {decision}")
                    else:
                        st.warning(f"### ⚠️ Decision Status: {decision} (Manual Hand-off)")
                        
                    # 2. Confidence Indicator Gauge
                    st.metric(label="🎯 System Certainty Score", value=f"{int(confidence * 100)}%")
                    st.progress(float(confidence))
                    
                    # 3. Context Assessment Details Breakdown
                    st.markdown("#### 📝 Determination Summary & Reason")
                    st.info(explanation)
                    
                    # 4. Sequential Workflow Audit Logs Breakdown
                    with st.expander("📜 System Engine Audit Trail Logs"):
                        for idx, step in enumerate(logs):
                            st.write(f"**[{idx+1}]** {step}")
                            
                except Exception as e:
                    st.error(f"❌ Structural Processing Pipeline Error: {str(e)}")
    else:
        st.caption("Awaiting claim submission profile data input to run analysis.")
