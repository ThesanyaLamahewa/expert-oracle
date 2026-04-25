"""
app.py — Expert Oracle: Knowledge Immortalization Agent
--------------------------------------------------------
v2.4 — Feature 1: URL Intelligence Ingestion
       Feature 2: Document Intelligence Ingestion
       Feature 3: YouTube Intelligence Ingestion
       Feature 4: Knowledge Conflict Detector
"""

import streamlit as st
import os
import json
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

if not os.environ.get("GROQ_API_KEY"):
    st.set_page_config(page_title="Expert Oracle", page_icon="🧠")
    st.error(
        "### ❌ GROQ_API_KEY not found\n\n"
        f"Make sure your `.env` file exists at: `{env_path}`\n\n"
        "It should contain exactly one line:\n\n"
        "```\nGROQ_API_KEY=your_key_here\n```"
    )
    st.stop()

from agents.interviewer      import InterviewerAgent
from agents.extractor        import KnowledgeExtractor
from agents.twin             import ExpertTwin
from agents.explainer        import ExplainerAgent
from agents.counterfactual   import CounterfactualAgent
from agents.web_ingestor     import WebIngestor
from agents.doc_ingestor     import DocIngestor
from agents.youtube_ingestor import YouTubeIngestor
from agents.conflict_detector import ConflictDetector   # ── NEW Feature 4
from memory.store            import KnowledgeStore


# ════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Expert Oracle — Decision Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

.eo-hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem; font-weight: 700;
    background: linear-gradient(135deg, #F59E0B, #FCD34D 50%, #38BDF8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.1; margin: 0;
}
.eo-mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: #484F58;
}
.eo-story {
    background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(14,165,233,0.08));
    border: 1px solid rgba(245,158,11,0.25); border-radius: 14px;
    padding: 22px 26px; margin: 1rem 0 1.5rem;
}
.eo-story-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: #F59E0B; margin-bottom: 12px;
}
.eo-story p {
    font-family: 'Inter', sans-serif; font-size: 0.95rem;
    color: #C9D1D9; line-height: 1.75; margin: 0 0 10px;
}
.eo-story .tagline {
    font-family: 'Playfair Display', serif; font-size: 1.2rem;
    color: #38BDF8; font-style: italic; margin: 0;
}
.eo-step {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 13px 15px; margin-bottom: 9px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 10px;
}
.eo-step-icon {
    font-size: 1.2rem; flex-shrink: 0; width: 38px; height: 38px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(245,158,11,0.08); border-radius: 8px;
}
.eo-step-title {
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
    color: #F59E0B; font-weight: 500; letter-spacing: 0.1em;
    text-transform: uppercase; margin: 0 0 4px;
}
.eo-step-body {
    font-family: 'Inter', sans-serif; font-size: 0.86rem;
    color: #8B949E; line-height: 1.5; margin: 0;
}
.eo-page-header {
    padding: 1.2rem 0 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 1.2rem;
}
.eo-page-title {
    font-family: 'Playfair Display', serif; font-size: 1.8rem;
    font-weight: 700; color: #F0F6FC; margin: 0; line-height: 1;
}
.eo-page-sub {
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
    color: #484F58; letter-spacing: 0.12em; text-transform: uppercase; margin: 6px 0 0;
}
.eo-nugget-count {
    font-family: 'Playfair Display', serif; font-size: 2.4rem;
    font-weight: 700; color: #F59E0B; text-align: right; line-height: 1;
}
.eo-count-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    color: #484F58; letter-spacing: 0.1em; text-transform: uppercase;
}
.eo-card {
    border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;
    border-left-width: 3px; border-left-style: solid;
    border-top: 1px solid rgba(255,255,255,0.07);
    border-right: 1px solid rgba(255,255,255,0.07);
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.eo-card-doc {
    font-family: 'Inter', sans-serif; font-size: 0.9rem;
    color: #E6EDF3; line-height: 1.6; margin: 8px 0 0;
}
.eo-logic {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 10px 14px; margin-top: 10px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.76rem;
    color: #8B949E; line-height: 1.7;
}
.eo-badge {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase;
    padding: 2px 8px; border-radius: 4px;
    display: inline-block; margin-right: 6px; margin-bottom: 4px;
}
.eo-explanation {
    background: rgba(52,211,153,0.05); border-left: 3px solid #34D399;
    border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 8px 0;
    font-family: 'Inter', sans-serif; font-size: 0.86rem;
    color: #C9D1D9; line-height: 1.7;
}
.eo-expl-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.63rem;
    color: #34D399; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 8px;
}
.eo-cf {
    background: rgba(248,113,113,0.05); border-left: 3px solid #F87171;
    border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 8px 0;
    font-family: 'Inter', sans-serif; font-size: 0.86rem;
    color: #C9D1D9; line-height: 1.7;
}
.eo-cf-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.63rem;
    color: #F87171; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 8px;
}
.eo-active-bar {
    background: linear-gradient(90deg, rgba(14,165,233,0.08), rgba(245,158,11,0.08));
    border: 1px solid rgba(14,165,233,0.2); border-radius: 8px;
    padding: 10px 16px; font-family: 'Inter', sans-serif;
    font-size: 0.87rem; color: #8B949E; line-height: 1.5; margin-bottom: 1.2rem;
}
.eo-source-card {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;
    font-family: 'Inter', sans-serif; font-size: 0.78rem;
    color: #6B7280; line-height: 1.5;
}
.eo-source-title {
    color: #8B949E; font-weight: 500; margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
}
.eo-tone-tag {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    color: #38BDF8; background: rgba(56,189,248,0.08);
    padding: 3px 8px; border-radius: 4px; margin: 2px; display: inline-block;
}
.eo-summary-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 7px 11px; margin-bottom: 5px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05); border-radius: 7px;
}
.eo-summary-label { font-family: 'Inter', sans-serif; font-size: 0.82rem; color: #8B949E; }
.eo-summary-val { font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 700; }
.eo-ingest-box {
    background: rgba(14,165,233,0.05); border: 1px solid rgba(14,165,233,0.2);
    border-radius: 10px; padding: 12px 16px; margin: 0.5rem 0;
}
.eo-ingest-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.15em; text-transform: uppercase; color: #38BDF8; margin-bottom: 4px;
}
.eo-doc-box {
    background: rgba(167,139,250,0.05); border: 1px solid rgba(167,139,250,0.2);
    border-radius: 10px; padding: 12px 16px; margin: 0.5rem 0;
}
.eo-doc-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.15em; text-transform: uppercase; color: #A78BFA; margin-bottom: 4px;
}
.eo-yt-box {
    background: rgba(248,113,113,0.05); border: 1px solid rgba(248,113,113,0.2);
    border-radius: 10px; padding: 12px 16px; margin: 0.5rem 0;
}
.eo-yt-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.15em; text-transform: uppercase; color: #F87171; margin-bottom: 4px;
}
.eo-ingest-result {
    background: rgba(52,211,153,0.06); border: 1px solid rgba(52,211,153,0.2);
    border-radius: 8px; padding: 10px 14px;
    font-family: 'Inter', sans-serif; font-size: 0.84rem;
    color: #C9D1D9; line-height: 1.6; margin-top: 8px;
}
.eo-warn-box {
    background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.2);
    border-radius: 8px; padding: 10px 14px;
    font-family: 'Inter', sans-serif; font-size: 0.82rem;
    color: #C9D1D9; line-height: 1.6; margin-top: 6px;
}
/* ── NEW: Conflict cards ── */
.eo-conflict-card {
    border-radius: 10px; padding: 16px 18px; margin-bottom: 12px;
    border-left: 3px solid #F59E0B;
    background: rgba(245,158,11,0.05);
    border-top: 1px solid rgba(245,158,11,0.15);
    border-right: 1px solid rgba(245,158,11,0.15);
    border-bottom: 1px solid rgba(245,158,11,0.15);
}
.eo-conflict-card.high {
    border-left-color: #F87171;
    background: rgba(248,113,113,0.05);
    border-top-color: rgba(248,113,113,0.15);
    border-right-color: rgba(248,113,113,0.15);
    border-bottom-color: rgba(248,113,113,0.15);
}
.eo-conflict-card.low {
    border-left-color: #6EE7B7;
    background: rgba(110,231,183,0.05);
    border-top-color: rgba(110,231,183,0.15);
    border-right-color: rgba(110,231,183,0.15);
    border-bottom-color: rgba(110,231,183,0.15);
}
.eo-conflict-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 10px; display: flex; align-items: center; gap: 8px;
}
.eo-conflict-nugget {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;
    font-family: 'Inter', sans-serif; font-size: 0.84rem;
    color: #C9D1D9; line-height: 1.55;
}
.eo-conflict-vs {
    text-align: center; font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; color: #484F58; margin: 4px 0; letter-spacing: 0.1em;
}
.eo-conflict-resolution {
    background: rgba(56,189,248,0.06); border: 1px solid rgba(56,189,248,0.2);
    border-radius: 8px; padding: 10px 12px; margin-top: 8px;
    font-family: 'Inter', sans-serif; font-size: 0.82rem;
    color: #8B949E; line-height: 1.55;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# DESIGN CONSTANTS
# ════════════════════════════════════════════════════════════════
TYPE_CFG = {
    "decision_rule":  {"color": "#A78BFA", "bg": "rgba(167,139,250,0.1)",  "label": "Decision Rule"},
    "mental_model":   {"color": "#34D399", "bg": "rgba(52,211,153,0.1)",   "label": "Mental Model"},
    "heuristic":      {"color": "#38BDF8", "bg": "rgba(56,189,248,0.1)",   "label": "Heuristic"},
    "lesson_learned": {"color": "#F59E0B", "bg": "rgba(245,158,11,0.1)",   "label": "Lesson Learned"},
    "process":        {"color": "#6EE7B7", "bg": "rgba(110,231,183,0.1)",  "label": "Process"},
    "warning":        {"color": "#F87171", "bg": "rgba(248,113,113,0.1)",  "label": "Warning"},
}
CONF_CFG = {
    "high":   {"color": "#34D399", "bg": "rgba(52,211,153,0.1)"},
    "medium": {"color": "#F59E0B", "bg": "rgba(245,158,11,0.1)"},
    "low":    {"color": "#8B949E", "bg": "rgba(139,148,158,0.1)"},
}
SEVERITY_CFG = {
    "high":   {"color": "#F87171", "label": "HIGH CONFLICT"},
    "medium": {"color": "#F59E0B", "label": "MEDIUM CONFLICT"},
    "low":    {"color": "#6EE7B7", "label": "LOW TENSION"},
}


def tbadge(ktype):
    c = TYPE_CFG.get(ktype, {"color": "#8B949E", "bg": "rgba(139,148,158,0.1)", "label": ktype})
    return (f'<span class="eo-badge" style="color:{c["color"]};background:{c["bg"]}">'
            f'{c["label"]}</span>')

def cbadge(level):
    c = CONF_CFG.get(level, CONF_CFG["medium"])
    return (f'<span class="eo-badge" style="color:{c["color"]};background:{c["bg"]}">'
            f'{level} confidence</span>')

def knowledge_card_html(doc, meta, show_logic=True):
    ktype = meta.get("type", "knowledge")
    logic = meta.get("decision_logic", "")
    conf  = meta.get("confidence_level", "medium")
    past  = json.loads(meta.get("past_situations", "[]"))
    cfg   = TYPE_CFG.get(ktype, {"color": "#8B949E", "bg": "rgba(139,148,158,0.05)"})

    logic_html = ""
    if show_logic and logic:
        cl = (logic
              .replace("IF ",      '<span style="color:#38BDF8;font-weight:600">IF</span> ')
              .replace("THEN ",    '<span style="color:#34D399;font-weight:600">THEN</span> ')
              .replace("BECAUSE ", '<span style="color:#F59E0B;font-weight:600">BECAUSE</span> '))
        logic_html = f'<div class="eo-logic">{cl}</div>'

    past_html = ""
    if past:
        items = "".join(f'<li style="margin-bottom:3px;color:#6B7280">{p}</li>' for p in past)
        past_html = (f'<ul style="margin:8px 0 0;padding-left:18px;'
                     f'font-size:0.78rem;color:#6B7280">{items}</ul>')

    source = meta.get("source_question", "")
    source_badge = ""
    if source.startswith("http"):
        d = source.split("/")[2][:40]
        source_badge = (f'<span class="eo-badge" style="color:#38BDF8;'
                        f'background:rgba(56,189,248,0.08)">🌐 {d}</span>')
    elif source.startswith("document:"):
        fname = source.replace("document:", "").strip()[:35]
        source_badge = (f'<span class="eo-badge" style="color:#A78BFA;'
                        f'background:rgba(167,139,250,0.08)">📄 {fname}</span>')
    elif source.startswith("youtube:"):
        ytitle = source.replace("youtube:", "").strip()[:35]
        source_badge = (f'<span class="eo-badge" style="color:#F87171;'
                        f'background:rgba(248,113,113,0.08)">▶ {ytitle}</span>')

    return (f'<div class="eo-card" style="background:{cfg["bg"]};border-left-color:{cfg["color"]}">'
            f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px">'
            f'{tbadge(ktype)}{cbadge(conf)}{source_badge}</div>'
            f'<p class="eo-card-doc">{doc}</p>'
            f'{logic_html}{past_html}</div>')


def conflict_card_html(conflict):
    """Render a conflict detection card."""
    severity = conflict.get("severity", "medium")
    scfg     = SEVERITY_CFG.get(severity, SEVERITY_CFG["medium"])
    css_cls  = severity  # high / medium / low maps to CSS class

    source_a = conflict.get("source_a", "interview")
    source_b = conflict.get("source_b", "interview")

    # Clean up source labels for display
    def fmt_source(s):
        if s.startswith("http"):
            return "🌐 " + s.split("/")[2][:30]
        elif s.startswith("document:"):
            return "📄 " + s.replace("document:", "").strip()[:30]
        elif s.startswith("youtube:"):
            return "▶ " + s.replace("youtube:", "").strip()[:30]
        else:
            return "🎤 interview"

    label_a = fmt_source(source_a)
    label_b = fmt_source(source_b)

    return (
        f'<div class="eo-conflict-card {css_cls}">'
        f'<div class="eo-conflict-label">'
        f'<span style="color:{scfg["color"]}">{scfg["label"]}</span>'
        f'<span style="color:#484F58">{conflict.get("explanation", "")}</span>'
        f'</div>'
        f'<div class="eo-conflict-nugget">'
        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.6rem;'
        f'color:#484F58;text-transform:uppercase;letter-spacing:0.08em">{label_a}</span><br>'
        f'{conflict["nugget_a"]}</div>'
        f'<div class="eo-conflict-vs">⟷ CONFLICTS WITH ⟷</div>'
        f'<div class="eo-conflict-nugget">'
        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.6rem;'
        f'color:#484F58;text-transform:uppercase;letter-spacing:0.08em">{label_b}</span><br>'
        f'{conflict["nugget_b"]}</div>'
        f'<div class="eo-conflict-resolution">'
        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.6rem;'
        f'color:#38BDF8;text-transform:uppercase;letter-spacing:0.08em">'
        f'🔧 RESOLUTION</span><br>{conflict.get("resolution", "")}</div>'
        f'</div>'
    )


# ════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════
DEFAULTS = {
    "page":                "setup",
    "expert_name":         "",
    "domain":              "",
    "chat_history":        [],
    "twin_history":        [],
    "knowledge_count":     0,
    "interviewer":         None,
    "extractor":           None,
    "store":               None,
    "twin":                None,
    "explainer":           None,
    "cf_agent":            None,
    "conflict_detector":   None,    # ── NEW Feature 4
    "conflicts":           [],      # ── NEW: stored conflict results
    "tone_built":          False,
    "last_question":       "",
    "last_recommendation": "",
    "last_sources":        [],
    "web_ingestor":        None,
    "doc_ingestor":        None,
    "yt_ingestor":         None,
    "ingest_summary":      "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ════════════════════════════════════════════════════════════════
# PAGE 1 — SETUP
# ════════════════════════════════════════════════════════════════
if st.session_state.page == "setup":

    col_logo, col_title = st.columns([1, 11])
    with col_logo:
        st.markdown(
            '<div style="width:52px;height:52px;border-radius:12px;'
            'background:linear-gradient(135deg,#D97706,#0EA5E9);'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:1.6rem;box-shadow:0 0 24px rgba(245,158,11,0.3);'
            'margin-top:8px">🧠</div>',
            unsafe_allow_html=True,
        )
    with col_title:
        st.markdown(
            '<p class="eo-hero-title">Expert Oracle</p>'
            '<p class="eo-mono" style="margin:4px 0 0">Decision Intelligence System &nbsp;·&nbsp; '
            'Knowledge Immortalization Agent &nbsp;·&nbsp; v2.4</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="eo-story">
      <div class="eo-story-label">&#9679; The problem this solves</div>
      <p><strong style="color:#F0F6FC">Friday 5pm.</strong>
         Dr. Margaret Chen — Senior Financial Analyst, 25 years, three recessions survived —
         clears her desk and retires. With her goes every pricing instinct, every crisis heuristic,
         every <em>"I've seen this before"</em> that no meeting, no document, no knowledge base captured.</p>
      <p><strong style="color:#F0F6FC">Monday 9am.</strong>
         The board faces a pricing crisis. Raw materials up 34%.
         Competitor just cut prices 12%. The new analysts have models. They don't have judgment.</p>
      <p class="tagline">What if they could still ask Margaret?</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col_form, col_how = st.columns([1, 1], gap="large")

    with col_form:
        st.subheader("Start a new session")

        if st.button("⚡  Load Margaret Chen demo scenario", use_container_width=True):
            st.session_state["_demo"] = True

        demo = st.session_state.get("_demo", False)

        expert_name = st.text_input(
            "Expert's full name",
            value="Dr. Margaret Chen" if demo else "",
            placeholder="e.g. Dr. Margaret Chen",
        )
        domain = st.text_input(
            "Domain of expertise",
            value="Corporate Financial Strategy and Pricing" if demo else "",
            placeholder="e.g. Corporate Financial Strategy and Pricing",
        )
        st.text_input(
            "Role / context (optional)",
            value="Senior Financial Analyst · 25 years · three recessions navigated" if demo else "",
            placeholder="e.g. Senior Financial Analyst, 25 years",
        )

        # Feature 1 — URL
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="eo-ingest-box"><div class="eo-ingest-label">🌐 URL Intelligence Ingestion — optional</div></div>', unsafe_allow_html=True)
        url_input = st.text_area(
            "Paste links about this expert — one per line",
            placeholder="https://en.wikipedia.org/wiki/...\nhttps://www.forbes.com/profile/...",
            height=90,
        )
        st.caption("Supports: Wikipedia · news articles · HBR · Forbes · any public webpage.")

        # Feature 2 — Documents
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="eo-doc-box"><div class="eo-doc-label">📄 Document Intelligence Ingestion — optional</div></div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload documents about this expert",
            type=["pdf", "docx", "txt", "csv"],
            accept_multiple_files=True,
        )
        if uploaded_files:
            st.caption(f"Ready: {', '.join(f.name for f in uploaded_files)}")

        # Feature 3 — YouTube
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="eo-yt-box"><div class="eo-yt-label">▶ YouTube Intelligence Ingestion — optional</div></div>', unsafe_allow_html=True)
        yt_input = st.text_area(
            "Paste YouTube video links — one per line",
            placeholder="https://www.youtube.com/watch?v=...\nhttps://youtu.be/...",
            height=90,
        )
        st.caption("Talks · interviews · lectures · keynotes. Requires captions enabled.")

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        if st.button("🚀  Begin knowledge capture", type="primary", use_container_width=True):
            if expert_name.strip() and domain.strip():
                n = expert_name.strip()
                d = domain.strip()

                st.session_state.expert_name       = n
                st.session_state.domain            = d
                st.session_state.store             = KnowledgeStore(n)
                st.session_state.interviewer       = InterviewerAgent()
                st.session_state.extractor         = KnowledgeExtractor()
                st.session_state.explainer         = ExplainerAgent(n, d)
                st.session_state.cf_agent          = CounterfactualAgent(n, d)
                st.session_state.web_ingestor      = WebIngestor()
                st.session_state.doc_ingestor      = DocIngestor()
                st.session_state.yt_ingestor       = YouTubeIngestor()
                st.session_state.conflict_detector = ConflictDetector(n, d)   # ── NEW
                st.session_state.conflicts         = []

                ingest_messages = []

                # URL ingestion
                urls = [u.strip() for u in url_input.strip().splitlines() if u.strip()]
                if urls:
                    with st.spinner(f"🌐 Reading {len(urls)} URL{'s' if len(urls)>1 else ''}…"):
                        url_result = st.session_state.web_ingestor.ingest(urls=urls, expert_name=n, domain=d)
                    for nugget in url_result["nuggets"]:
                        st.session_state.store.add_knowledge(
                            content=nugget.get("content", ""),
                            knowledge_type=nugget.get("type", "lesson_learned"),
                            source_question=nugget.get("source", "web"),
                            decision_logic=nugget.get("decision_logic", ""),
                            past_situations=nugget.get("past_situations", []),
                            confidence_level=nugget.get("confidence_level", "medium"),
                        )
                    if url_result["total"] > 0:
                        ingest_messages.append(f"🌐 {url_result['total']} nuggets from {len(url_result['sources'])} URL{'s' if len(url_result['sources'])>1 else ''}")
                    for w in url_result["warnings"]:
                        ingest_messages.append(w)

                # Document ingestion
                if uploaded_files:
                    file_label = f"{len(uploaded_files)} file{'s' if len(uploaded_files)>1 else ''}"
                    with st.spinner(f"📄 Reading {file_label}…"):
                        doc_result = st.session_state.doc_ingestor.ingest(uploaded_files=uploaded_files, expert_name=n, domain=d)
                    for nugget in doc_result["nuggets"]:
                        st.session_state.store.add_knowledge(
                            content=nugget.get("content", ""),
                            knowledge_type=nugget.get("type", "lesson_learned"),
                            source_question=nugget.get("source", "document"),
                            decision_logic=nugget.get("decision_logic", ""),
                            past_situations=nugget.get("past_situations", []),
                            confidence_level=nugget.get("confidence_level", "medium"),
                        )
                    if doc_result["total"] > 0:
                        ingest_messages.append(f"📄 {doc_result['total']} nuggets from {len(doc_result['sources'])} document{'s' if len(doc_result['sources'])>1 else ''} ({', '.join(doc_result['sources'])})")
                    for w in doc_result["warnings"]:
                        ingest_messages.append(w)

                # YouTube ingestion
                yt_urls = [u.strip() for u in yt_input.strip().splitlines() if u.strip()]
                if yt_urls:
                    with st.spinner(f"▶ Reading {len(yt_urls)} video transcript{'s' if len(yt_urls)>1 else ''}…"):
                        yt_result = st.session_state.yt_ingestor.ingest(youtube_urls=yt_urls, expert_name=n, domain=d)
                    for nugget in yt_result["nuggets"]:
                        st.session_state.store.add_knowledge(
                            content=nugget.get("content", ""),
                            knowledge_type=nugget.get("type", "lesson_learned"),
                            source_question=nugget.get("source", "youtube"),
                            decision_logic=nugget.get("decision_logic", ""),
                            past_situations=nugget.get("past_situations", []),
                            confidence_level=nugget.get("confidence_level", "medium"),
                        )
                    if yt_result["total"] > 0:
                        ingest_messages.append(f"▶ {yt_result['total']} nuggets from {len(yt_result['sources'])} video{'s' if len(yt_result['sources'])>1 else ''}")
                    for w in yt_result["warnings"]:
                        ingest_messages.append(w)

                st.session_state.knowledge_count = st.session_state.store.count()

                if ingest_messages:
                    total = st.session_state.knowledge_count
                    st.session_state.ingest_summary = (
                        f"✅ {total} knowledge nuggets pre-loaded before the interview started.\n\n"
                        + "\n".join(ingest_messages)
                        + "\n\nThe interview will now probe deeper into what was already discovered."
                    )
                else:
                    st.session_state.ingest_summary = ""

                opening = st.session_state.interviewer.start_interview(n, d)
                st.session_state.chat_history = [("assistant", opening)]
                st.session_state.page = "interview"
                st.rerun()
            else:
                st.error("Please enter the expert's name and their domain.")

    with col_how:
        st.subheader("How it works")
        steps = [
            ("🌐", "URL Ingestion", "Paste links — Wikipedia, news, company bios. Pre-loads knowledge before the interview begins."),
            ("📄", "Document Upload", "Upload PDFs, Word docs, TXT, CSV. Board reports, papers, memos — extracted automatically."),
            ("▶",  "YouTube Ingestion", "Paste a YouTube talk or interview. Transcript fetched and expertise extracted."),
            ("🎤", "Interview", "Structured AI interviewer extracts WHAT the expert decided and WHY — the tacit reasoning."),
            ("⚙️", "Extract", "Every answer decomposed into IF → THEN → BECAUSE decision logic automatically."),
            ("🔍", "Conflict Detection", "Scans the knowledge base for contradictions — where the expert said opposite things at different times."),
            ("🧠", "Expert Twin", "Answers in the expert's voice with explanation layer and counterfactual reasoning."),
        ]
        for icon, title, body in steps:
            st.markdown(
                f'<div class="eo-step"><div class="eo-step-icon">{icon}</div>'
                f'<div><p class="eo-step-title">{title}</p>'
                f'<p class="eo-step-body">{body}</p></div></div>',
                unsafe_allow_html=True,
            )


# ════════════════════════════════════════════════════════════════
# PAGE 2 — INTERVIEW
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "interview":

    hc1, hc2 = st.columns([5, 1])
    with hc1:
        st.markdown(
            f'<div class="eo-page-header">'
            f'<p class="eo-page-title">🎤 {st.session_state.expert_name}</p>'
            f'<p class="eo-page-sub">Interview in progress &nbsp;·&nbsp; {st.session_state.domain}</p>'
            f'</div>', unsafe_allow_html=True,
        )
    with hc2:
        st.markdown(
            f'<div style="text-align:right;padding-top:1.2rem">'
            f'<div class="eo-nugget-count">{st.session_state.knowledge_count}</div>'
            f'<div class="eo-count-label">nuggets</div></div>',
            unsafe_allow_html=True,
        )

    if st.session_state.ingest_summary:
        lines       = st.session_state.ingest_summary.split("\n\n")
        success_ln  = lines[0] if lines else ""
        detail_ln   = lines[1] if len(lines) > 1 else ""
        probe_ln    = lines[2] if len(lines) > 2 else ""
        if success_ln:
            items_html = "".join(
                f'<span style="display:block;margin-top:4px">{i}</span>'
                for i in detail_ln.split("\n") if i.strip()
            )
            probe_html = (f'<div style="margin-top:6px;font-size:0.82rem;color:#6B7280;font-style:italic">{probe_ln}</div>'
                          if probe_ln else "")
            st.markdown(
                f'<div class="eo-ingest-result">'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:0.62rem;'
                f'color:#34D399;letter-spacing:0.1em;text-transform:uppercase;'
                f'display:block;margin-bottom:6px">✅ Knowledge pre-loaded</span>'
                f'{success_ln}<div style="margin-top:6px;font-size:0.8rem;color:#8B949E">{items_html}</div>'
                f'{probe_html}</div>',
                unsafe_allow_html=True,
            )

    col_chat, col_panel = st.columns([2, 1], gap="large")

    with col_chat:
        chat_box = st.container(height=460)
        with chat_box:
            for role, msg in st.session_state.chat_history:
                with st.chat_message(role, avatar="🤖" if role == "assistant" else "👤"):
                    st.write(msg)

        user_input = st.chat_input(f"Answer as {st.session_state.expert_name}…")

        if user_input:
            st.session_state.chat_history.append(("user", user_input))
            last_q = next(
                (m for r, m in reversed(st.session_state.chat_history[:-1]) if r == "assistant"), ""
            )
            with st.spinner("Extracting decision logic…"):
                nuggets = st.session_state.extractor.extract(last_q, user_input)
                for n in nuggets:
                    st.session_state.store.add_knowledge(
                        content=n.get("content", user_input),
                        knowledge_type=n.get("type", "lesson_learned"),
                        source_question=last_q,
                        decision_logic=n.get("decision_logic", ""),
                        past_situations=n.get("past_situations", []),
                        confidence_level=n.get("confidence_level", "medium"),
                    )
                st.session_state.knowledge_count = st.session_state.store.count()
            with st.spinner("Preparing next question…"):
                nxt = st.session_state.interviewer.respond(user_input)
                st.session_state.chat_history.append(("assistant", nxt))
            st.rerun()

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("✅  Build the Expert Twin", type="primary", use_container_width=True):
                if st.session_state.knowledge_count >= 5:
                    with st.spinner("Building voice profile and initialising twin…"):
                        tx = st.session_state.interviewer.get_transcript()
                        tp = st.session_state.extractor.build_tone_profile(tx)
                        st.session_state.store.save_tone_profile(tp)
                        st.session_state.twin = ExpertTwin(
                            st.session_state.expert_name,
                            st.session_state.domain,
                            st.session_state.store,
                        )
                        st.session_state.tone_built = True
                    st.session_state.page = "twin"
                    st.rerun()
                else:
                    st.warning(f"Answer at least 5 questions first. Current: {st.session_state.knowledge_count} nuggets.")
        with b2:
            if st.button("📚  View knowledge archive", use_container_width=True):
                st.session_state.page = "knowledge"
                st.rerun()

    with col_panel:
        st.subheader("Live extraction")
        st.progress(min(st.session_state.knowledge_count / 25, 1.0))
        st.caption(f"{st.session_state.knowledge_count} of 25 target nuggets")

        if st.session_state.store and st.session_state.knowledge_count > 0:
            all_k = st.session_state.store.get_all()
            if all_k["documents"]:
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                st.markdown('<p class="eo-mono" style="margin-bottom:8px">Latest captures</p>', unsafe_allow_html=True)
                docs  = all_k["documents"][-3:]
                metas = all_k["metadatas"][-3:]
                for doc, meta in zip(reversed(docs), reversed(metas)):
                    st.markdown(knowledge_card_html(doc[:200]+"…", meta, show_logic=True), unsafe_allow_html=True)
        else:
            st.caption("Answer the first question to see decision logic extracted in real time.")


# ════════════════════════════════════════════════════════════════
# PAGE 3 — KNOWLEDGE ARCHIVE
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "knowledge":

    st.markdown(
        f'<div class="eo-page-header">'
        f'<p class="eo-page-title">📚 Knowledge Archive</p>'
        f'<p class="eo-page-sub">{st.session_state.expert_name} &nbsp;·&nbsp; '
        f'{st.session_state.knowledge_count} structured nuggets &nbsp;·&nbsp; '
        f'{st.session_state.domain}</p></div>',
        unsafe_allow_html=True,
    )

    # ── Tabs: Archive | Conflicts ─────────────────────────────────
    tab_archive, tab_conflicts = st.tabs(["📋  Knowledge Archive", "🔍  Conflict Detection"])

    with tab_archive:
        col_main, col_side = st.columns([3, 1], gap="large")

        with col_main:
            if st.session_state.store and st.session_state.knowledge_count > 0:
                all_k = st.session_state.store.get_all()
                fc1, fc2 = st.columns([2, 1])
                with fc1:
                    tf = st.selectbox("Filter by type", ["All"] + list(TYPE_CFG.keys()))
                with fc2:
                    sl = st.toggle("Show IF/THEN/BECAUSE", value=True)

                visible = 0
                for doc, meta in zip(all_k["documents"], all_k["metadatas"]):
                    ktype = meta.get("type", "knowledge")
                    if tf != "All" and ktype != tf:
                        continue
                    visible += 1
                    st.markdown(knowledge_card_html(doc, meta, sl), unsafe_allow_html=True)
                st.caption(f"Showing {visible} of {st.session_state.knowledge_count} nuggets")
            else:
                st.info("No knowledge captured yet.")

        with col_side:
            st.subheader("Summary")
            if st.session_state.store and st.session_state.knowledge_count > 0:
                all_k = st.session_state.store.get_all()
                counts: dict = {}
                for m in all_k["metadatas"]:
                    t = m.get("type", "unknown")
                    counts[t] = counts.get(t, 0) + 1
                for t, n in sorted(counts.items(), key=lambda x: -x[1]):
                    cfg = TYPE_CFG.get(t, {"color": "#8B949E"})
                    st.markdown(
                        f'<div class="eo-summary-row">'
                        f'<span class="eo-summary-label">{t.replace("_"," ").title()}</span>'
                        f'<span class="eo-summary-val" style="color:{cfg["color"]}">{n}</span>'
                        f'</div>', unsafe_allow_html=True,
                    )

            if st.session_state.tone_built:
                tone = st.session_state.store.get_tone_profile()
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                st.markdown('<p class="eo-mono" style="color:#F59E0B;margin-bottom:8px">Voice profile</p>', unsafe_allow_html=True)
                for marker in tone.get("tone_markers", [])[:6]:
                    st.markdown(f'<span class="eo-tone-tag">{marker}</span>', unsafe_allow_html=True)
                st.markdown("")

            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            if st.button("← Back to interview", use_container_width=True):
                st.session_state.page = "interview"
                st.rerun()
            if st.session_state.knowledge_count >= 5:
                if st.button("🧠  Consult the Expert Twin →", type="primary", use_container_width=True):
                    if not st.session_state.twin:
                        with st.spinner("Initialising twin…"):
                            tx = st.session_state.interviewer.get_transcript()
                            tp = st.session_state.extractor.build_tone_profile(tx)
                            st.session_state.store.save_tone_profile(tp)
                            st.session_state.twin = ExpertTwin(
                                st.session_state.expert_name,
                                st.session_state.domain,
                                st.session_state.store,
                            )
                            st.session_state.tone_built = True
                    st.session_state.page = "twin"
                    st.rerun()

    # ── NEW: CONFLICT DETECTION TAB ──────────────────────────────
    with tab_conflicts:
        st.markdown(
            '<p class="eo-mono" style="margin-bottom:8px;color:#F59E0B">'
            '🔍 Knowledge conflict detector</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="eo-active-bar">'
            'Scans the entire knowledge base for contradictions — where the expert said opposite or '
            'incompatible things across different sessions or sources. '
            'Conflicts are flagged with severity levels and resolution guidance, '
            'so the Expert Twin can acknowledge evolving thinking rather than presenting '
            'a false consistency.'
            '</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.knowledge_count < 6:
            st.info("Build a larger knowledge base first — at least 6 nuggets needed for meaningful conflict detection.")
        else:
            col_btn, col_info = st.columns([1, 3])
            with col_btn:
                scan_btn = st.button(
                    "🔍  Scan for conflicts",
                    type="primary",
                    use_container_width=True,
                )
            with col_info:
                if st.session_state.conflicts:
                    st.caption(
                        f"Last scan found {len(st.session_state.conflicts)} conflict"
                        f"{'s' if len(st.session_state.conflicts) != 1 else ''}. "
                        f"Rescan anytime after adding more knowledge."
                    )

            if scan_btn:
                with st.spinner(
                    f"Scanning {st.session_state.knowledge_count} nuggets for contradictions… "
                    f"This may take 20-40 seconds."
                ):
                    st.session_state.conflicts = st.session_state.conflict_detector.scan(
                        st.session_state.store
                    )
                st.rerun()

            if st.session_state.conflicts:
                high   = [c for c in st.session_state.conflicts if c.get("severity") == "high"]
                medium = [c for c in st.session_state.conflicts if c.get("severity") == "medium"]
                low    = [c for c in st.session_state.conflicts if c.get("severity") == "low"]

                # Summary metrics
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.metric("🔴 High conflicts",   len(high))
                with mc2:
                    st.metric("🟡 Medium conflicts", len(medium))
                with mc3:
                    st.metric("🟢 Low tensions",     len(low))

                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

                # Display all conflicts
                for conflict in st.session_state.conflicts:
                    st.markdown(conflict_card_html(conflict), unsafe_allow_html=True)

            elif not scan_btn:
                st.markdown(
                    '<div style="text-align:center;padding:2rem;color:#484F58;'
                    'font-family:Inter,sans-serif;font-size:0.88rem">'
                    'Click "Scan for conflicts" to analyse the knowledge base.<br>'
                    'The system will check every nugget pair for semantic contradictions.'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.success(
                    "✅ No contradictions detected. The knowledge base is internally consistent."
                )


# ════════════════════════════════════════════════════════════════
# PAGE 4 — EXPERT TWIN
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "twin":

    markers_line = ""
    if st.session_state.tone_built and st.session_state.store:
        t = st.session_state.store.get_tone_profile()
        markers_line = " &nbsp;·&nbsp; " + " · ".join(t.get("tone_markers", [])[:4])

    # Conflict awareness line
    conflict_note = ""
    if st.session_state.conflicts:
        n_conflicts = len(st.session_state.conflicts)
        conflict_note = (
            f" &nbsp;·&nbsp; "
            f'<span style="color:#F59E0B">'
            f'{n_conflicts} known conflict{"s" if n_conflicts != 1 else ""} in knowledge base'
            f'</span>'
        )

    st.markdown(
        f'<div class="eo-page-header" style="display:flex;align-items:center;gap:14px">'
        f'<div style="width:46px;height:46px;border-radius:50%;flex-shrink:0;'
        f'background:linear-gradient(135deg,#D97706,#0EA5E9);'
        f'display:flex;align-items:center;justify-content:center;font-size:1.3rem;'
        f'box-shadow:0 0 20px rgba(245,158,11,0.3)">🧠</div>'
        f'<div>'
        f'<p class="eo-page-title">{st.session_state.expert_name}</p>'
        f'<p class="eo-page-sub">Expert Twin &nbsp;·&nbsp; {st.session_state.knowledge_count} nuggets'
        f'{markers_line}{conflict_note}</p></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="eo-active-bar">✅ &nbsp;Decision intelligence active. '
        'Every answer draws on stored decision logic and reasoning patterns. '
        'Use the <strong>counterfactual button</strong> after any answer to explore the alternative timeline.</div>',
        unsafe_allow_html=True,
    )

    col_main, col_side = st.columns([2, 1], gap="large")

    with col_main:
        twin_box = st.container(height=380)
        with twin_box:
            if not st.session_state.twin_history:
                with st.chat_message("assistant", avatar="🧠"):
                    # ── NEW: mention conflict awareness if conflicts exist
                    conflict_msg = ""
                    if st.session_state.conflicts:
                        n = len(st.session_state.conflicts)
                        conflict_msg = (
                            f" I am also aware of {n} area"
                            f"{'s' if n != 1 else ''} where my thinking has evolved or "
                            f"contains tension — I will flag these when relevant."
                        )
                    st.write(
                        f"Hello. I am the Expert Twin of {st.session_state.expert_name}. "
                        f"I carry their decision logic, mental models, and reasoning patterns "
                        f"in {st.session_state.domain}."
                        f"{conflict_msg} "
                        f"Ask me anything — I will give you their recommendation, the reasoning "
                        f"behind it, and what would have happened if you chose differently."
                    )

            for item in st.session_state.twin_history:
                role = item["role"]
                msg  = item["message"]
                if role == "user":
                    with st.chat_message("user", avatar="❓"):
                        st.write(msg)
                else:
                    with st.chat_message("assistant", avatar="🧠"):
                        st.write(msg)
                    if item.get("explanation"):
                        st.markdown(
                            f'<div class="eo-explanation">'
                            f'<div class="eo-expl-label">⚡ Explanation layer</div>'
                            f'{item["explanation"]}</div>',
                            unsafe_allow_html=True,
                        )
                    if item.get("counterfactual"):
                        st.markdown(
                            f'<div class="eo-cf">'
                            f'<div class="eo-cf-label">⚠️ Counterfactual analysis — the alternative timeline</div>'
                            f'{item["counterfactual"]}</div>',
                            unsafe_allow_html=True,
                        )

        query = st.chat_input(f"Ask {st.session_state.expert_name}'s twin…")

        if query:
            st.session_state.twin_history.append({"role": "user", "message": query})
            st.session_state.last_question = query
            with st.spinner("Consulting stored knowledge…"):
                answer, sources = st.session_state.twin.ask(query)
            with st.spinner("Generating explanation layer…"):
                tp   = st.session_state.store.get_tone_profile()
                expl = st.session_state.explainer.generate(
                    question=query, recommendation=answer, sources=sources, tone=tp,
                )
            st.session_state.twin_history.append({
                "role": "assistant", "message": answer,
                "sources": sources, "explanation": expl, "counterfactual": "",
            })
            st.session_state.last_recommendation = answer
            st.session_state.last_sources        = sources
            st.rerun()

        if any(i["role"] == "assistant" for i in st.session_state.twin_history):
            if st.button("⚠️  What would have happened if we hadn't followed this advice?", use_container_width=True):
                with st.spinner("Reasoning through the counterfactual timeline…"):
                    tp = st.session_state.store.get_tone_profile()
                    cf = st.session_state.cf_agent.reason(
                        question=st.session_state.last_question,
                        recommendation=st.session_state.last_recommendation,
                        sources=st.session_state.last_sources,
                        tone=tp,
                    )
                for i in reversed(range(len(st.session_state.twin_history))):
                    if st.session_state.twin_history[i]["role"] == "assistant":
                        st.session_state.twin_history[i]["counterfactual"] = cf
                        break
                st.rerun()

    with col_side:
        st.markdown('<p class="eo-mono" style="margin-bottom:10px">Knowledge sources</p>', unsafe_allow_html=True)

        last_sources = next(
            (i["sources"] for i in reversed(st.session_state.twin_history)
             if i["role"] == "assistant" and i.get("sources")),
            []
        )
        if last_sources:
            for src in last_sources[:4]:
                lines = src.split("\n")
                title = lines[0][:70] if lines else ""
                body  = " ".join(lines[1:])[:160] if len(lines) > 1 else ""
                st.markdown(
                    f'<div class="eo-source-card">'
                    f'<div class="eo-source-title">{title}</div>'
                    f'{body}…</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Ask a question to see retrieved sources here.")

        if st.session_state.tone_built:
            tone = st.session_state.store.get_tone_profile()
            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            st.markdown('<p class="eo-mono" style="color:#F59E0B;margin-bottom:8px">Active voice profile</p>', unsafe_allow_html=True)
            st.caption(tone.get("communication_style", "")[:180])
            for marker in tone.get("tone_markers", [])[:6]:
                st.markdown(f'<span class="eo-tone-tag">{marker}</span>', unsafe_allow_html=True)
            st.markdown("")

        # Show conflict summary if any
        if st.session_state.conflicts:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.markdown('<p class="eo-mono" style="color:#F59E0B;margin-bottom:6px">Known conflicts</p>', unsafe_allow_html=True)
            for c in st.session_state.conflicts[:3]:
                severity = c.get("severity", "medium")
                dot_color = {"high": "#F87171", "medium": "#F59E0B", "low": "#6EE7B7"}.get(severity, "#F59E0B")
                st.markdown(
                    f'<div style="font-size:0.78rem;color:#6B7280;padding:4px 0;'
                    f'border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:4px">'
                    f'<span style="color:{dot_color}">●</span> '
                    f'{c.get("explanation","")[:80]}…</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        if st.button("📚  Knowledge archive",  use_container_width=True):
            st.session_state.page = "knowledge"
            st.rerun()
        if st.button("🎤  Continue interview", use_container_width=True):
            st.session_state.page = "interview"
            st.rerun()
        if st.button("🔄  New expert",         use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()