import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient
from agents import (
    AgentExecutionError,
    scheme_researcher_agent,
    eligibility_analyzer_agent,
    scheme_guide_writer_agent,
    judge_agent,
    fallback_research_brief,
    fallback_eligibility_analysis,
    fallback_scheme_guide,
    fallback_judge_result,
)

load_dotenv()

st.set_page_config(
    page_title="SchemeSaathi | Smart Government Scheme Finder",
    page_icon="🇮🇳",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --primary: #1a5fb4;
    --primary-container: #3584e4;
    --primary-fixed: #99c1f1;
    --secondary: #5c6166;
    --secondary-container: #dde3ea;
    --tertiary: #e66100;
    --background: #f8f9fc;
    --surface-low: #f0f3f8;
    --surface-high: #e2e8f0;
    --surface-lowest: #ffffff;
    --on-surface: #1a1d21;
    --on-surface-variant: #2c3a4a;
    --outline-variant: #bec6d0;
}

.stApp {
    background: var(--background) !important;
    font-family: 'Manrope', sans-serif !important;
    color: var(--on-surface) !important;
}

[data-testid="stSidebar"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
.main .block-container {
    max-width: 100% !important;
    padding: 0 !important;
}

/* NAV */
.app-nav {
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 999;
    background: rgba(248,249,252,0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(190,198,208,0.2);
}

.app-brand {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--primary);
    letter-spacing: -0.03em;
}

.app-brand span {
    color: var(--tertiary);
}

.app-nav-links {
    display: flex;
    gap: 2rem;
    align-items: center;
    font-size: 0.9rem;
    font-weight: 500;
}

.nav-active {
    color: var(--primary);
    font-weight: 700;
    border-bottom: 2px solid var(--primary);
    padding-bottom: 2px;
}

.nav-muted { color: var(--secondary); }

/* HERO */
.app-hero {
    padding: 7rem 2rem 5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(26,95,180,0.14) 0%, transparent 70%),
        radial-gradient(ellipse 50% 40% at 20% 30%, rgba(53,132,228,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 80% 20%, rgba(230,97,0,0.10) 0%, transparent 60%),
        linear-gradient(180deg, rgba(153,193,241,0.2) 0%, rgba(248,249,252,1) 55%);
    border-bottom: 1px solid rgba(53,132,228,0.1);
}

.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.5rem, 6vw, 5rem);
    font-weight: 800;
    color: var(--on-surface);
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin-bottom: 1.2rem;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: var(--on-surface-variant);
    max-width: 40rem;
    margin: 0 auto 1.5rem;
    line-height: 1.7;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(26,95,180,0.08);
    border: 1px solid rgba(53,132,228,0.3);
    border-radius: 999px;
    padding: 0.65rem 1.2rem;
    font-size: 0.88rem;
    color: var(--primary);
    font-weight: 600;
    backdrop-filter: blur(8px);
}

/* INPUT SECTION */
.input-section {
    max-width: 1100px;
    margin: 0 auto;
    padding: 3rem 2rem;
}

.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    text-align: center;
    color: var(--on-surface);
    margin-bottom: 0.5rem;
}

.section-sub {
    text-align: center;
    color: var(--on-surface-variant);
    font-size: 0.95rem;
    margin-bottom: 2.5rem;
    line-height: 1.6;
}

.input-card {
    background: var(--surface-lowest);
    border-radius: 20px;
    padding: 1.6rem;
    box-shadow: 0 20px 40px rgba(26,29,33,0.06);
    margin-bottom: 1.2rem;
}

.input-card-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--on-surface);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.input-note {
    font-size: 0.8rem;
    color: var(--on-surface-variant);
    margin-top: 0.6rem;
}

/* Streamlit textarea */
.stTextArea textarea {
    background: var(--surface-low) !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.95rem !important;
    color: var(--on-surface) !important;
    min-height: 120px !important;
    resize: vertical !important;
    box-shadow: none !important;
}

.stTextArea textarea::placeholder {
    color: #2c3a4a !important;
    opacity: 0.6 !important;
}

.stTextArea textarea:focus {
    box-shadow: 0 0 0 2px rgba(53,132,228,0.3) !important;
    outline: none !important;
}

.stTextArea label { display: none !important; }

/* Streamlit select */
.stSelectbox > div {
    background: var(--surface-low) !important;
    border: none !important;
    border-radius: 14px !important;
}

.stSelectbox label { display: none !important; }

/* CTA Button */
.stButton > button {
    width: 100% !important;
    min-height: 3.5rem !important;
    border-radius: 999px !important;
    border: none !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-container) 100%) !important;
    color: white !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 16px 32px rgba(26,95,180,0.25) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 20px 40px rgba(26,95,180,0.32) !important;
}

/* PROGRESS */
.progress-shell {
    max-width: 800px;
    margin: 0 auto 3rem;
    background: var(--surface-low);
    border-radius: 24px;
    padding: 2rem;
}

.progress-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 1rem;
}

.progress-label-text {
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--primary);
    margin-bottom: 0.3rem;
}

.progress-title-text {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--on-surface);
}

.progress-pct {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--on-surface);
}

.progress-track {
    width: 100%;
    height: 10px;
    background: rgba(26,29,33,0.06);
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 1.2rem;
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--primary), var(--primary-container));
    transition: width 0.4s ease;
}

.progress-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.progress-item {
    font-size: 0.88rem;
    color: var(--on-surface-variant);
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.progress-item.done { color: var(--primary); font-weight: 600; }

.log-box {
    background: rgba(255,255,255,0.7);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-top: 1rem;
    font-size: 0.88rem;
    color: var(--on-surface-variant);
    line-height: 1.8;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: transparent !important;
    border-bottom: none !important;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 999px !important;
    height: 2.8rem !important;
    padding: 0 1.2rem !important;
    background: var(--surface-low) !important;
    border: none !important;
    color: var(--on-surface) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
}

.stTabs [aria-selected="true"] {
    background: var(--surface-lowest) !important;
    color: var(--primary) !important;
    box-shadow: 0 8px 20px rgba(26,29,33,0.07) !important;
}

.stTabs [data-baseweb="tab-panel"] {
    background: var(--surface-lowest) !important;
    border-radius: 20px !important;
    padding: 1.5rem !important;
    box-shadow: 0 20px 40px rgba(26,29,33,0.05) !important;
}

/* SCORE CARD */
.score-card {
    background: var(--surface-lowest);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 24px 48px rgba(26,29,33,0.07);
    position: sticky;
    top: 5rem;
}

.score-kicker {
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--on-surface-variant);
    text-align: center;
    margin-bottom: 1rem;
}

.score-ring-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    margin-bottom: 0.75rem;
    height: 132px;
}

.score-ring-number {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #1a1d21;
    line-height: 1;
}

.score-match-label {
    text-align: center;
    font-weight: 700;
    color: var(--tertiary);
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

.metric-row { margin-bottom: 1rem; }

.metric-top {
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--on-surface);
    margin-bottom: 0.35rem;
}

.mini-bar {
    width: 100%;
    height: 8px;
    border-radius: 999px;
    background: var(--surface-high);
    overflow: hidden;
}

.mini-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: var(--primary-container);
}

.score-note {
    font-size: 0.88rem;
    color: var(--on-surface-variant);
    line-height: 1.6;
    margin-top: 0.5rem;
}

.score-divider {
    border: none;
    border-top: 1px solid rgba(190,198,208,0.2);
    margin: 1.25rem 0;
}

.blueprint-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: rgba(53,132,228,0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
}

.blueprint-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--on-surface);
}

/* FOOTER */
.app-footer {
    background: var(--surface-high);
    padding: 3rem 2rem;
    text-align: center;
    margin-top: 4rem;
}

.footer-copy {
    color: var(--secondary);
    font-size: 0.82rem;
    line-height: 1.6;
    max-width: 40rem;
    margin: 0 auto 1rem;
    opacity: 0.8;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    font-size: 0.82rem;
    color: var(--secondary);
}

.footer-links a {
    color: var(--primary);
    text-decoration: underline;
    opacity: 0.8;
}

/* Profile summary card */
.profile-card {
    background: linear-gradient(135deg, rgba(26,95,180,0.07), rgba(53,132,228,0.04));
    border: 1px solid rgba(53,132,228,0.15);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
    line-height: 1.8;
    color: var(--on-surface-variant);
}

.profile-card strong {
    color: var(--primary);
}

/* Scheme badge */
.scheme-count-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(230,97,0,0.1);
    border: 1px solid rgba(230,97,0,0.25);
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--tertiary);
    margin-left: 0.75rem;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<nav class="app-nav">
    <div class="app-brand">Scheme<span>Saathi</span> 🇮🇳</div>
    <div class="app-nav-links">
        <span class="nav-active">Find Schemes</span>
        <span class="nav-muted">How It Works</span>
        <span class="nav-muted">Help</span>
    </div>
</nav>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<section class="app-hero">
    <div style="
        position:absolute;top:4rem;left:10%;
        width:320px;height:320px;
        background:radial-gradient(circle, rgba(53,132,228,0.15) 0%, transparent 70%);
        border-radius:50%;pointer-events:none;">
    </div>
    <div style="
        position:absolute;top:2rem;right:8%;
        width:240px;height:240px;
        background:radial-gradient(circle, rgba(230,97,0,0.12) 0%, transparent 70%);
        border-radius:50%;pointer-events:none;">
    </div>
    <div style="position:relative;z-index:1;">
        <div style="
            display:inline-flex;align-items:center;gap:0.5rem;
            background:rgba(26,95,180,0.08);
            border:1px solid rgba(53,132,228,0.25);
            border-radius:999px;padding:0.4rem 1rem;
            font-size:0.8rem;font-weight:700;color:#1a5fb4;
            letter-spacing:0.08em;text-transform:uppercase;
            margin-bottom:1.2rem;">
            🤖 AI-Powered · Real Schemes Only
        </div>
        <h1 class="hero-title">🇮🇳 Smart Government<br>Scheme Finder</h1>
        <p class="hero-subtitle">
            Tell us about yourself. Our AI finds every Indian government scheme you're eligible for
            — and guides you step-by-step to apply.
        </p>
        <div class="hero-pill">
            ✅ Only real, verifiable schemes from official gov.in sources
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# ── INPUT SECTION ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="input-section">
    <h2 class="section-title">Your Profile</h2>
    <p class="section-sub">
        Fill in your details accurately. The more specific you are, the more precisely
        we can match you to schemes you actually qualify for.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="input-card">
        <div class="input-card-label">👤 Basic Details</div>
    </div>
    """, unsafe_allow_html=True)

    age = st.text_area(
        "age",
        placeholder="Age: e.g. 28",
        height=60,
        label_visibility="collapsed",
        key="age_input",
    )
    gender = st.selectbox(
        "gender",
        ["Select Gender", "Male", "Female", "Transgender", "Prefer not to say"],
        label_visibility="collapsed",
        key="gender_input",
    )
    state = st.text_area(
        "state",
        placeholder="State & District: e.g. Maharashtra, Pune",
        height=80,
        label_visibility="collapsed",
        key="state_input",
    )
    st.markdown('<div class="input-note">💡 State matters — many schemes are state-specific.</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="input-card">
        <div class="input-card-label">💼 Socio-Economic Details</div>
    </div>
    """, unsafe_allow_html=True)

    occupation = st.text_area(
        "occupation",
        placeholder="Occupation: e.g. Farmer, Daily wage labourer, Student, Small business owner, Unemployed",
        height=80,
        label_visibility="collapsed",
        key="occupation_input",
    )
    income = st.text_area(
        "income",
        placeholder="Annual family income: e.g. Below ₹1 lakh, ₹1-3 lakh, ₹3-6 lakh",
        height=80,
        label_visibility="collapsed",
        key="income_input",
    )
    category = st.selectbox(
        "category",
        ["Select Category", "General", "OBC", "SC", "ST", "EWS", "Minority", "Other"],
        label_visibility="collapsed",
        key="category_input",
    )
    st.markdown('<div class="input-note">💡 Caste category helps us find reservation-based schemes.</div>', unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="input-card">
        <div class="input-card-label">📋 Additional Details</div>
    </div>
    """, unsafe_allow_html=True)

    education = st.text_area(
        "education",
        placeholder="Education level: e.g. Class 10 pass, Graduate, Currently in Class 12",
        height=80,
        label_visibility="collapsed",
        key="education_input",
    )
    special = st.text_area(
        "special",
        placeholder="Special conditions (if any): e.g. Differently abled, BPL card holder, Widow, Pregnant woman, No pucca house",
        height=100,
        label_visibility="collapsed",
        key="special_input",
    )
    st.markdown('<div class="input-note">💡 Special conditions often unlock additional targeted schemes.</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    find_btn = st.button("🔍 Find My Eligible Schemes", type="primary")

# ── PIPELINE ──────────────────────────────────────────────────────────────────
if find_btn:
    # Validate required fields
    if not age or not state or not occupation or not income:
        st.warning("Please fill in at least Age, State, Occupation, and Income before searching.")
        st.stop()

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    tavily_key = os.getenv("TAVILY_API_KEY", "")

    if not tavily_key:
        st.error("TAVILY_API_KEY is missing in your .env file.")
        st.stop()

    gender_val = gender if gender != "Select Gender" else "Not specified"
    category_val = category if category != "Select Category" else "Not specified"

    user_profile = f"""Age: {age}
Gender: {gender_val}
State: {state}
Occupation: {occupation}
Income Range: {income}
Caste Category: {category_val}
Education Level: {education or "Not specified"}
Special Conditions: {special or "None"}"""

    client = genai.Client(api_key=gemini_key, vertexai=False) if gemini_key else None
    tavily_client = TavilyClient(api_key=tavily_key)

    # Show profile summary
    special_str = f" · {special}" if special else ""
    st.markdown(
        f'<div style="max-width:1100px;margin:1.5rem auto 0;padding:0 2rem">'
        f'<div class="profile-card">'
        f'<strong>Your Profile:</strong> {age}-year-old {gender_val} from {state} · '
        f'{occupation} · Income: {income} · Category: {category_val}{special_str}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    logs = []
    fallback_messages = []
    progress_value = 10
    progress_placeholder = st.empty()

    def render_progress():
        steps = [
            ("🔍 Searching for schemes",        progress_value >= 35),
            ("✅ Checking your eligibility",    progress_value >= 60),
            ("📋 Writing application guides",   progress_value >= 82),
            ("⭐ Evaluating accuracy",           progress_value >= 100),
        ]
        items_html = "".join(
            f'<div class="progress-item {"done" if done else ""}">'
            f'{"✓" if done else "○"} {label}</div>'
            for label, done in steps
        )
        log_html = (
            f'<div class="log-box">{"<br>".join(logs[-6:])}</div>'
            if logs else ""
        )
        progress_placeholder.markdown(f"""
        <div class="progress-shell">
            <div class="progress-header">
                <div>
                    <div class="progress-label-text">AI Agent Pipeline</div>
                    <div class="progress-title-text">Finding your schemes...</div>
                </div>
                <div class="progress-pct">{progress_value}%</div>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{progress_value}%"></div>
            </div>
            <div class="progress-grid">{items_html}</div>
            {log_html}
        </div>
        """, unsafe_allow_html=True)

    def log_step(msg):
        logs.append(f"✓ {msg}")
        render_progress()

    def record_fallback(message):
        if message not in fallback_messages:
            fallback_messages.append(message)

    render_progress()

    # Agent 1: Researcher
    with st.spinner(""):
        if client is None:
            log_step("Researcher: Gemini unavailable — using Tavily fallback")
            research_brief = fallback_research_brief(tavily_client, user_profile)
            record_fallback("Researcher ran in fallback mode.")
        else:
            try:
                research_brief = scheme_researcher_agent(client, tavily_client, user_profile, log_step=log_step)
            except AgentExecutionError as e:
                log_step("Researcher: fallback mode")
                research_brief = fallback_research_brief(tavily_client, user_profile)
                record_fallback(e.user_message)
    progress_value = 35
    render_progress()

    # Agent 2: Eligibility Analyzer
    with st.spinner(""):
        if client is None:
            log_step("Eligibility Analyzer: using built-in matching")
            eligibility_analysis = fallback_eligibility_analysis(research_brief, user_profile)
            record_fallback("Eligibility Analyzer ran in fallback mode.")
        else:
            try:
                eligibility_analysis = eligibility_analyzer_agent(client, research_brief, user_profile, log_step=log_step)
            except AgentExecutionError as e:
                log_step("Eligibility Analyzer: fallback mode")
                eligibility_analysis = fallback_eligibility_analysis(research_brief, user_profile)
                record_fallback(e.user_message)
    progress_value = 60
    render_progress()

    # Agent 3: Guide Writer
    with st.spinner(""):
        if client is None:
            log_step("Guide Writer: using built-in templates")
            scheme_guide = fallback_scheme_guide(research_brief, eligibility_analysis, user_profile)
            record_fallback("Guide Writer ran in fallback mode.")
        else:
            try:
                scheme_guide = scheme_guide_writer_agent(client, research_brief, eligibility_analysis, user_profile, log_step=log_step)
            except AgentExecutionError as e:
                log_step("Guide Writer: fallback mode")
                scheme_guide = fallback_scheme_guide(research_brief, eligibility_analysis, user_profile)
                record_fallback(e.user_message)
    progress_value = 82
    render_progress()

    # Agent 4: Judge
    with st.spinner(""):
        if client is None:
            log_step("Judge: using estimated rubric")
            judge_result = fallback_judge_result()
            record_fallback("Judge ran in fallback mode.")
        else:
            try:
                judge_result = judge_agent(client, user_profile, research_brief, scheme_guide, log_step=log_step)
            except AgentExecutionError as e:
                log_step("Judge: fallback mode")
                judge_result = fallback_judge_result()
                record_fallback(e.user_message)
    progress_value = 100
    render_progress()
    progress_placeholder.empty()

    # Fallback messages suppressed — agents handle gracefully without user-facing warnings

    # ── OUTPUT ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="max-width:1200px;margin:2rem auto;padding:0 2rem">
        <div style="display:flex;align-items:center;gap:0.85rem;margin-bottom:1.5rem">
            <div class="blueprint-icon">🎯</div>
            <div class="blueprint-title">Your Eligible Schemes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    output_col, score_col = st.columns([1.9, 0.95], gap="large")

    with output_col:
        tabs = st.tabs(["🔍 Found Schemes", "✅ Eligibility Check", "📋 How to Apply", "⭐ Quality Score"])

        with tabs[0]:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#1a5fb4,#3584e4);color:white;
                        border-radius:18px;padding:1.3rem;margin-bottom:1rem">
                <h3 style="color:white;font-family:'Plus Jakarta Sans',sans-serif;
                           font-size:1.2rem;margin-bottom:0.25rem">
                    Schemes Found For Your Profile
                </h3>
                <p style="color:rgba(255,255,255,0.8);font-size:0.88rem">
                    Based on your profile — searched across central and state schemes
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(research_brief)

        with tabs[1]:
            st.markdown(eligibility_analysis)

        with tabs[2]:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#e66100,#f5841f);color:white;
                        border-radius:18px;padding:1.3rem;margin-bottom:1rem">
                <h3 style="color:white;font-family:'Plus Jakarta Sans',sans-serif;
                           font-size:1.2rem;margin-bottom:0.25rem">
                    Step-by-Step Application Guide
                </h3>
                <p style="color:rgba(255,255,255,0.8);font-size:0.88rem">
                    For each scheme you're eligible for — documents, steps, and official links
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(scheme_guide)

        with tabs[3]:
            st.markdown(judge_result.get("summary", ""))
            st.markdown("---")
            labels = {
                "accuracy":          "Accuracy",
                "eligibility_match": "Eligibility Match",
                "completeness":      "Completeness",
                "clarity":           "Clarity",
                "relevance":         "Relevance",
            }
            for key, label in labels.items():
                data  = judge_result.get("scores", {}).get(key, {})
                score = float(data.get("score", 0))
                st.markdown(f"**{label}** — {score}/5")
                st.progress(min(max(score / 5, 0.0), 1.0))
                st.caption(data.get("reasoning", ""))

    with score_col:
        overall  = float(judge_result.get("overall_score", 0))
        pct      = min(int(round((overall / 5) * 100)), 100)
        match_label = (
            "Highly Reliable"  if pct >= 85 else
            "Reliable"         if pct >= 70 else
            "Indicative"
        )
        scores   = judge_result.get("scores", {})
        accuracy = int((float(scores.get("accuracy",          {}).get("score", 0)) / 5) * 100)
        match    = int((float(scores.get("eligibility_match", {}).get("score", 0)) / 5) * 100)
        clarity  = int((float(scores.get("clarity",           {}).get("score", 0)) / 5) * 100)
        offset_val = round(351.8 - (pct / 100) * 351.8, 1)
        top_strength    = judge_result.get("top_strength", "")
        top_improvement = judge_result.get("top_improvement", "")

        st.markdown(f"""
<div class="score-card">
    <div class="score-kicker">Recommendation Quality Score</div>
    <div class="score-ring-wrapper">
        <svg width="132" height="132" viewBox="0 0 132 132"
             xmlns="http://www.w3.org/2000/svg"
             style="transform:rotate(-90deg)">
            <circle cx="66" cy="66" r="56" stroke="#e2e8f0"
                    stroke-width="8" fill="transparent"/>
            <circle cx="66" cy="66" r="56" stroke="#1a5fb4"
                    stroke-width="8" fill="transparent"
                    stroke-dasharray="351.8"
                    stroke-dashoffset="{offset_val}"
                    stroke-linecap="round"/>
        </svg>
        <div class="score-ring-number">{pct}</div>
    </div>
    <div class="score-match-label">{match_label}</div>
    <div class="metric-row">
        <div class="metric-top"><span>Scheme Accuracy</span><span>{accuracy}%</span></div>
        <div class="mini-bar">
            <div class="mini-bar-fill" style="width:{accuracy}%"></div>
        </div>
    </div>
    <div class="metric-row">
        <div class="metric-top"><span>Eligibility Match</span><span>{match}%</span></div>
        <div class="mini-bar">
            <div class="mini-bar-fill" style="width:{match}%"></div>
        </div>
    </div>
    <div class="metric-row">
        <div class="metric-top"><span>Clarity</span><span>{clarity}%</span></div>
        <div class="mini-bar">
            <div class="mini-bar-fill" style="width:{clarity}%"></div>
        </div>
    </div>
    <hr class="score-divider"/>
    <div class="score-note"><strong>Strength:</strong> {top_strength}</div>
    <div class="score-note" style="margin-top:0.75rem">
        <strong>To Improve:</strong> {top_improvement}
    </div>
    <hr class="score-divider"/>
    <div class="score-note" style="font-size:0.78rem;opacity:0.75">
        ⚠️ Always verify scheme details on official gov.in portals before applying.
    </div>
</div>
""", unsafe_allow_html=True)

    st.success("🎉 Scheme search complete! Check the tabs above to see your eligible schemes and how to apply.")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<footer class="app-footer">
    <p class="footer-copy">
        © 2024 SchemeSaathi. This tool is for informational purposes only.
        Always verify eligibility and apply through official government portals (gov.in).
        This is not an official government service.
    </p>
    <div class="footer-links">
        <a href="https://myscheme.gov.in" target="_blank">MyScheme Portal</a>
        <a href="https://india.gov.in" target="_blank">India.gov.in</a>
        <span>Helpline: 1800-11-8002</span>
    </div>
</footer>
""", unsafe_allow_html=True)
