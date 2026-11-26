import ast
import html
import time

import streamlit as st

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
.steps {display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 18px;}
.steps .card {flex: 1; min-width: 200px; margin: 0;}
.num {display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center;
      border-radius: 50%; background: #4F46E5; color: #fff; font-weight: 700; margin-right: 8px;}
.verdict {animation: rise .5s ease-out;}
@keyframes rise {from {opacity: 0; transform: translateY(12px);} to {opacity: 1; transform: none;}}
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
    """Builds or loads the vector database once per container."""
    try:
        from rag.retriever import get_vector_store
        get_vector_store()
    except Exception as e:
        return f"ERROR: {e}"
    return "OK"


with st.spinner("Preparing the policy knowledge base..."):
    store_status = initialize_vector_store()
if store_status.startswith("ERROR"):
    st.error(f"Document ingestion failed. {store_status}")

from graph import app_engine


PROGRESS = {
    "retrieve": "🔎 Found related policy clauses",
    "grader": "🧪 Checked that the clauses are relevant",
    "rewrite": "✍️ Refined the search",
    "websearch": "🌐 Searched the web for more information",
    "adjudicate": "⚖️ Assessed the coverage",
    "hallucination": "🛡️ Verified the reasoning",
    "escalate": "👤 Prepared a handover for a claims officer",
}


def run_claim(claim_text, progress):
    """Runs the workflow, reporting each step as it finishes."""
    state = {
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
    for event in app_engine.stream(dict(state), stream_mode="updates"):
        for node, update in event.items():
            progress.write(PROGRESS.get(node, node))
            state.update(update or {})
    state["_seconds"] = time.time() - start
    return state


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


NEXT_STEPS = {
    "Covered": "Keep your bills, photos and reports ready, then submit them to your insurer for verification.",
    "Not Covered": "Read the reasoning and cited clauses. If something is missing from your description, add it and try again.",
    "Escalate": "A claims officer needs to review this case. Download the report and share it with them.",
}


def build_report(result, citations):
    lines = [
        "CLAIMFORGE AI - ASSESSMENT REPORT",
        "AI-assisted output. A claims officer should confirm the final decision.",
        "",
        f"Claim: {result.get('claim', '')}",
        f"Decision: {result.get('decision', '')}",
        f"Model confidence: {float(result.get('confidence', 0)):.0%}",
        "",
        "Reasoning:",
        str(result.get("final_answer", "")),
        "",
        "Evidence cited:",
        *(f"- {c}" for c in citations),
        "",
        "Audit trail:",
        *(f"{n}. {s}" for n, s in enumerate(result.get("audit_trail", []), 1)),
    ]
    return "\n".join(lines)


def open_past(item):
    st.session_state.result = item
    st.session_state.claim_text = item["claim"]


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
    st.subheader("🕘 Recent claims")
    history_box = st.container()
    st.divider()
    st.caption("AI-assisted output. A claims officer should confirm any final decision.")

st.markdown(
    '<div class="hero"><h1>🛡️ ClaimForge AI</h1>'
    '<p>Describe a claim and get a policy-backed coverage assessment.</p>'
    '<span class="chip">🏠 Home</span><span class="chip">🏥 Health</span>'
    '<span class="chip">🚗 Accident</span><span class="chip">❤️ Life</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="steps">'
    '<div class="card"><span class="num">1</span><b>Describe</b><br>Tell us what happened, or pick an example.</div>'
    '<div class="card"><span class="num">2</span><b>Analyze</b><br>Watch each check as it completes.</div>'
    '<div class="card"><span class="num">3</span><b>Review</b><br>See the decision and download the report.</div>'
    '</div>',
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
    words = len(user_claim.split())
    if 0 < words < 10:
        st.caption("💡 Add more detail: what happened, when, and which policy you hold.")
    else:
        st.caption(f"{words} words")
    submitted = st.button("🚀 Analyze claim", type="primary", use_container_width=True)
    st.button("Clear", on_click=clear_form, use_container_width=True)

with col_results:
    st.subheader("📊 Assessment")

    if submitted:
        st.session_state.pop("result", None)
        if not user_claim.strip():
            st.warning("Please enter a claim description first.")
        else:
            try:
                with st.status("Analyzing your claim...", expanded=True) as progress:
                    outcome = run_claim(user_claim, progress)
                    progress.update(label="Analysis complete", state="complete", expanded=False)
                st.session_state.result = outcome
                history = st.session_state.get("history", [])
                st.session_state.history = [outcome, *history][:5]
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

        st.info(f"**What to do next:** {NEXT_STEPS.get(decision, NEXT_STEPS['Escalate'])}")

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

        st.download_button(
            "⬇️ Download report",
            data=build_report(result, citations),
            file_name="claim_assessment.txt",
            use_container_width=True,
        )
        st.caption(f"Processed in {result.get('_seconds', 0):.1f} seconds")

# Filled last so a claim analyzed in this run appears straight away
with history_box:
    past = st.session_state.get("history", [])
    if not past:
        st.caption("Your analyzed claims will appear here.")
    for index, item in enumerate(past):
        icon = STYLES.get(item.get("decision"), STYLES["Escalate"])[0]
        st.button(f"{icon} {item['claim'][:32]}...", key=f"past_{index}",
                  on_click=open_past, args=(item,), use_container_width=True)
