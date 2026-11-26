import ast
import html
import os
import sys
import time

import streamlit as st

# Works whether this file sits in the repo root or inside Insurance_claim/
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) if os.path.basename(HERE) == "Insurance_claim" else HERE
sys.path.append(ROOT)

# Must be the first Streamlit call
st.set_page_config(page_title="ClaimForge AI — Adjudication Hub", page_icon="🛡️", layout="wide")


# ---------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------
st.markdown("""
<style>
.block-container {max-width: 1200px; padding-top: 3.5rem;}
.hero {background: linear-gradient(120deg, #1E1B4B 0%, #4F46E5 60%, #0EA5E9 100%);
       border-radius: 20px; padding: 32px 36px; margin-bottom: 22px; color: #fff;
       box-shadow: 0 12px 32px rgba(79,70,229,.25);}
.hero h1 {color: #fff; margin: 0; padding: 0; font-size: 2.1rem;}
.hero p {color: #E0E7FF; margin: 8px 0 16px;}
.chip {display: inline-block; background: rgba(255,255,255,.16); border-radius: 999px;
       padding: 4px 14px; margin: 0 8px 6px 0; font-size: .82rem;}
.card {background: #fff; color: #111827; border: 1px solid #E5E7EB; border-radius: 16px;
       padding: 20px 22px; margin-bottom: 14px; box-shadow: 0 4px 16px rgba(17,24,39,.05);}
.verdict {border-left: 8px solid var(--accent); background: var(--tint);}
.verdict .label {font-size: .85rem; color: #4B5563;}
.verdict .value {font-size: 1.8rem; font-weight: 700; color: var(--accent);}
.track {background: #E5E7EB; border-radius: 999px; height: 10px; margin-top: 10px; overflow: hidden;}
.fill {height: 100%; border-radius: 999px; background: var(--accent);}
.row {display: flex; justify-content: space-between; font-weight: 600;}
.cite {display: inline-block; background: #EEF2FF; color: #3730A3; border-radius: 8px;
       padding: 4px 10px; margin: 4px 6px 0 0; font-size: .82rem;}
.empty {text-align: center; color: #6B7280; border: 2px dashed #C7D2FE; padding: 56px 24px;}
.empty .icon {font-size: 2.6rem;}
div.stButton > button {border-radius: 12px; font-weight: 600;}
div.stButton > button[kind="primary"] {background: linear-gradient(90deg, #4F46E5, #0EA5E9);
       border: none; color: #fff; padding: .7rem 1rem;}
.stTextArea textarea {border-radius: 12px;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# BACKEND (same logic as before)
# ---------------------------------------------------------------------
@st.cache_resource
def initialize_vector_store():
    """Runs the ingestion check once per container."""
    db_path = "Insurance_claim/vector_db"
    if not os.path.exists(db_path) or len(os.listdir(db_path)) == 0:
        try:
            # The retriever expects this folder to exist; it indexes the PDFs if empty
            os.makedirs(db_path, exist_ok=True)
            from Insurance_claim.rag.retriever import get_vector_store
            get_vector_store()
        except Exception as e:
            return f"ERROR: {e}"
    return "OK"


with st.spinner("Preparing the policy knowledge base..."):
    store_status = initialize_vector_store()
if store_status.startswith("ERROR"):
    st.error(f"Document ingestion failed. {store_status}")

from Insurance_claim.graph import app_engine


def run_claim(claim_text):
    inputs = {
        "claim": claim_text,
        "query": None,
        "documents": [],
        "retry_count": 0,
        "relevance": "no",
        "decision": "Pending",
        "confidence": 0.0,
        "final_answer": "",
        "audit_trail": ["Workflow initialized via dashboard panel submission."],
    }
    start = time.time()
    result = app_engine.invoke(inputs)
    result["_seconds"] = time.time() - start
    return result


def parse_citations(value):
    """The adjudicate node stores citations as a stringified list in 'relevance'."""
    try:
        items = ast.literal_eval(value)
        return [str(i) for i in items] if isinstance(items, list) else []
    except (ValueError, SyntaxError, TypeError):
        return []


def as_html(text):
    return html.escape(str(text)).replace("\n", "<br>")


# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------
SAMPLES = {
    "🏠 Home": "My house suffered severe structural damage due to an earthquake. I am filing a claim for repairs.",
    "🏥 Health": "I was hospitalised for three days for an Ayurvedic Panchakarma treatment and want to claim the expenses.",
    "🚗 Accident": "I am a delivery rider and fractured my arm in a road accident while on duty.",
    "❤️ Life": "I am filing a term life claim after my father, the policyholder, passed away from a heart attack.",
}

STYLES = {  # decision: (icon, headline, accent colour, background tint)
    "Covered": ("✅", "Covered", "#047857", "#ECFDF5"),
    "Not Covered": ("❌", "Not Covered", "#B91C1C", "#FEF2F2"),
    "Escalate": ("⚠️", "Sent for human review", "#B45309", "#FFFBEB"),
}


def use_sample(text):
    st.session_state.claim_text = text
    st.session_state.pop("result", None)


def clear_form():
    use_sample("")


with st.sidebar:
    st.header("🛡️ ClaimForge AI")
    st.caption("Agentic claim adjudication")
    st.subheader("How it works")
    st.markdown(
        "1. 🔎 Retrieve policy clauses\n"
        "2. 🧪 Grade their relevance\n"
        "3. ✍️ Rewrite the query if needed\n"
        "4. ⚖️ Adjudicate the claim\n"
        "5. 🛡️ Verify the reasoning\n"
        "6. 👤 Escalate uncertain cases"
    )
    st.divider()
    st.caption("AI-assisted output. A claims officer should confirm any final decision.")

st.markdown(
    '<div class="hero"><h1>🛡️ ClaimForge AI</h1>'
    '<p>Describe a claim and get a policy-backed coverage assessment.</p>'
    '<span class="chip">🏠 Home</span><span class="chip">🏥 Health</span>'
    '<span class="chip">🚗 Accident</span><span class="chip">❤️ Life</span></div>',
    unsafe_allow_html=True,
)

col_input, col_results = st.columns([1, 1.2], gap="large")

with col_input:
    st.subheader("📋 Submit a claim")
    st.caption("Try an example:")
    for col, (label, text) in zip(st.columns(len(SAMPLES)), SAMPLES.items()):
        col.button(label, on_click=use_sample, args=(text,), use_container_width=True)

    user_claim = st.text_area(
        "Claim description",
        key="claim_text",
        placeholder="What happened, what was damaged or treated, and what are you claiming?",
        height=190,
    )
    submitted = st.button("🚀 Analyze claim", type="primary", use_container_width=True)
    st.button("Clear", on_click=clear_form, use_container_width=True)

with col_results:
    st.subheader("📊 Assessment")

    if submitted:
        st.session_state.pop("result", None)
        if not user_claim.strip():
            st.warning("Please enter a claim description first.")
        else:
            with st.spinner("Reviewing policies and adjudicating..."):
                try:
                    st.session_state.result = run_claim(user_claim)
                except Exception as e:
                    st.error(f"Processing failed: {e}")

    result = st.session_state.get("result")

    if result is None:
        st.markdown(
            '<div class="card empty"><div class="icon">🗂️</div>'
            '<b>No assessment yet</b><br>Submit a claim to see the decision here.</div>',
            unsafe_allow_html=True,
        )
    else:
        decision = result.get("decision", "Escalate")
        confidence = min(max(float(result.get("confidence", 0.0)), 0.0), 1.0)
        explanation = result.get("final_answer") or "No explanation returned."
        logs = result.get("audit_trail", [])
        citations = parse_citations(result.get("relevance"))
        icon, headline, accent, tint = STYLES.get(decision, STYLES["Escalate"])
        colours = f"--accent:{accent};--tint:{tint};"

        st.markdown(
            f'<div class="card verdict" style="{colours}"><div class="label">Decision</div>'
            f'<div class="value">{icon} {headline}</div></div>'
            f'<div class="card" style="{colours}"><div class="row"><span>Model confidence</span>'
            f'<span>{confidence:.0%}</span></div>'
            f'<div class="track"><div class="fill" style="width:{confidence:.0%}"></div></div></div>',
            unsafe_allow_html=True,
        )

        summary_tab, evidence_tab, audit_tab = st.tabs(["📝 Reasoning", "📚 Evidence", "📜 Audit trail"])
        with summary_tab:
            st.markdown(f'<div class="card">{as_html(explanation)}</div>', unsafe_allow_html=True)
        with evidence_tab:
            if citations:
                chips = "".join(f'<span class="cite">{as_html(c)}</span>' for c in citations)
                st.markdown(f'<div class="card">{chips}</div>', unsafe_allow_html=True)
            else:
                st.caption("No citations were returned for this claim.")
        with audit_tab:
            for number, step in enumerate(logs, 1):
                st.markdown(f'<div class="card"><b>Step {number}</b><br>{as_html(step)}</div>',
                            unsafe_allow_html=True)

        st.caption(f"Processed in {result.get('_seconds', 0):.1f} seconds")
