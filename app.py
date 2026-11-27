import ast
import base64
import html
import random
import time

import streamlit as st

# Must be the first Streamlit call
st.set_page_config(page_title="ClaimForge AI — Adjudication Hub", page_icon="🛡️", layout="wide")


# Original cartoon mascot, drawn in SVG so no image files are needed
MASCOT_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
<path d="M100 18 L170 44 V100 C170 144 138 172 100 188 C62 172 30 144 30 100 V44 Z"
 fill="#FFF7FD" stroke="#241C45" stroke-width="6" stroke-linejoin="round"/>
<ellipse cx="74" cy="92" rx="10" ry="14" fill="#241C45"/><circle cx="78" cy="86" r="4" fill="#fff"/>
<ellipse cx="126" cy="92" rx="10" ry="14" fill="#241C45"/><circle cx="130" cy="86" r="4" fill="#fff"/>
<ellipse cx="60" cy="118" rx="12" ry="7" fill="#FFB3D1"/><ellipse cx="140" cy="118" rx="12" ry="7" fill="#FFB3D1"/>
<path d="M84 120 Q100 138 116 120" fill="none" stroke="#241C45" stroke-width="6" stroke-linecap="round"/>
<path d="M176 14 l5 12 12 5 -12 5 -5 12 -5 -12 -12 -5 12 -5z" fill="#FFE7A3"/>
<path d="M20 140 l4 9 9 4 -9 4 -4 9 -4 -9 -9 -4 9 -4z" fill="#FFE7A3"/>
</svg>"""
MASCOT = "data:image/svg+xml;base64," + base64.b64encode(MASCOT_SVG.encode()).decode()


# Night City background, also drawn in code
def night_city():
    rng = random.Random(4)  # fixed seed: same skyline on every run
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 690" preserveAspectRatio="xMidYMax slice">',
        '<defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#0B1030"/>',
        '<stop offset="1" stop-color="#4B2A6E"/></linearGradient></defs>',
        '<rect width="1100" height="690" fill="url(#s)"/>',
    ]
    for _ in range(140):
        parts.append(f'<circle cx="{rng.randint(0, 1100)}" cy="{rng.randint(0, 420)}" '
                     f'r="{rng.choice([1, 1.5, 2.5])}" fill="#fff"/>')
    x = 0
    while x < 1100:
        width, height = rng.randint(50, 95), rng.randint(90, 260)
        parts.append(f'<rect x="{x}" y="{690 - height}" width="{width}" height="{height}" fill="#0A0C1E"/>')
        for wx in range(x + 8, x + width - 8, 16):
            for wy in range(690 - height + 12, 680, 22):
                if rng.random() < .35:
                    parts.append(f'<rect x="{wx}" y="{wy}" width="6" height="9" fill="#FFD36E"/>')
        x += width + 4
    parts.append("</svg>")
    return "data:image/svg+xml;base64," + base64.b64encode("".join(parts).encode()).decode()


# ---------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------
st.markdown(("""
<style>
.stApp {background: url("__CITY__") center bottom / cover fixed #12111C; color: #EEF1F8;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {background: #0C0C16; border-right: 1px solid #2B2B4A;}
.block-container {max-width: 1200px; padding-top: 3.5rem;}
.hero {display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap;
       background: linear-gradient(120deg, #5B00E0, #C4007A, #0066C8, #5B00E0); background-size: 300% 300%;
       animation: flow 12s ease infinite; border-radius: 24px; padding: 28px 36px; margin-bottom: 22px;
       box-shadow: 0 14px 40px rgba(196,0,122,.35);}
.hero h1 {color: #fff; margin: 0; padding: 0; font-size: 2.3rem;}
.hero p {color: #fff; margin: 8px 0 16px;}
.hero img {width: 170px; animation: float 4s ease-in-out infinite;}
.chip {display: inline-block; background: rgba(255,255,255,.18); color: #fff; border-radius: 999px;
       padding: 4px 14px; margin: 0 8px 6px 0; font-size: .82rem;}
.card {background: rgba(16,16,28,.92); color: #EEF1F8; border: 1px solid #2B2B4A; border-radius: 18px;
       padding: 20px 22px; margin-bottom: 14px; box-shadow: 0 6px 20px rgba(0,0,0,.28);}
.steps {display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 18px;}
.steps .card {flex: 1; min-width: 200px; margin: 0; border-top: 4px solid #00F5C4; transition: transform .2s;}
.steps .card:hover {transform: translateY(-5px);}
.steps .card:nth-child(1) {background: #16102B;}
.steps .card:nth-child(2) {background: #2A0E24;}
.steps .card:nth-child(3) {background: #08202E;}
.num {display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center;
      border-radius: 50%; background: #00F5C4; color: #07070D; font-weight: 700; margin-right: 8px;}
.verdict {border-left: 8px solid var(--accent); animation: rise .5s ease-out;}
.verdict .label {font-size: .85rem; color: #B7B3D1;}
.verdict .value {font-size: 1.8rem; font-weight: 700; color: var(--accent);}
.track {background: #34314D; border-radius: 999px; height: 10px; margin-top: 10px; overflow: hidden;}
.fill {height: 100%; border-radius: 999px; background: var(--accent); animation: grow 1s ease-out;}
.row {display: flex; justify-content: space-between; font-weight: 600;}
.cite {display: inline-block; background: #2A1B55; color: #00F5C4; border-radius: 8px;
       padding: 4px 10px; margin: 4px 6px 0 0; font-size: .82rem;}
.empty {text-align: center; color: #B7B3D1; border: 2px dashed #7A5CFF; padding: 56px 24px;}
.empty .icon {font-size: 2.8rem; animation: float 3s ease-in-out infinite;}
div.stButton > button, div.stDownloadButton > button {background: #10101C; color: #EEF1F8;
       border: 1px solid #00F5C4; border-radius: 12px; font-weight: 600; transition: transform .15s;}
div.stButton > button:hover, div.stDownloadButton > button:hover {border-color: #FF4FC3;
       color: #FF4FC3; transform: translateY(-2px);}
div.stButton > button[kind="primary"] {background: linear-gradient(90deg, #7A1FFF, #E0008C);
       border: none; color: #fff; padding: .7rem 1rem;}
div.stButton > button[kind="primary"]:hover {color: #fff;}
.stTextArea textarea {border-radius: 12px; background: #10101C;}
[data-testid="stExpander"], [data-testid="stAlert"], .stTabs [data-baseweb="tab-list"] {
       background: rgba(16,16,28,.92); border-radius: 12px;}
.stTabs [data-baseweb="tab-list"] {padding: 0 12px;}
@keyframes flow {0%, 100% {background-position: 0% 50%;} 50% {background-position: 100% 50%;}}
@keyframes float {0%, 100% {transform: translateY(0);} 50% {transform: translateY(-10px);}}
@keyframes rise {from {opacity: 0; transform: translateY(12px);} to {opacity: 1; transform: none;}}
@keyframes grow {from {width: 0;}}
@media (prefers-reduced-motion: reduce) {* {animation: none !important; transition: none !important;}}
</style>
""").replace("__CITY__", night_city()), unsafe_allow_html=True)


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
    "Covered": ("✅", "Covered", "#00F5C4", "#10101C"),
    "Not Covered": ("❌", "Not Covered", "#FF6B8B", "#10101C"),
    "Escalate": ("⚠️", "Sent for human review", "#FFD36E", "#10101C"),
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
    '<div class="hero"><div><h1>ClaimForge AI</h1>'
    '<p>Describe a claim and get a policy-backed coverage assessment.</p>'
    '<span class="chip">🏠 Home</span><span class="chip">🏥 Health</span>'
    '<span class="chip">🚗 Accident</span><span class="chip">❤️ Life</span></div>'
    f'<img src="{MASCOT}" alt="Smiling shield mascot"></div>',
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
                if outcome.get("decision") == "Covered":
                    st.balloons()
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
