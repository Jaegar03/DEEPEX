import asyncio
import streamlit as st
import os
import requests
import time
from dotenv import load_dotenv
from google import genai

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

/* ── Root variables ── */
:root {
  --bg:        #07091a;
  --surface:   #0d1230;
  --surface2:  #111840;
  --border:    rgba(0,212,255,0.18);
  --cyan:      #00d4ff;
  --cyan-dim:  rgba(0,212,255,0.12);
  --gold:      #f0a932;
  --text:      #c8d8f0;
  --text-dim:  #6a7fa8;
  --success:   #00e5a0;
  --error:     #ff5757;
  --radius:    12px;
}

/* ── Global resets ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Lora', Georgia, serif !important;
}

/* Animated star background */
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  background-image:
    radial-gradient(1px 1px at 12% 18%, rgba(255,255,255,0.55) 0%, transparent 100%),
    radial-gradient(1px 1px at 34% 72%, rgba(255,255,255,0.35) 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 56% 31%, rgba(0,212,255,0.45) 0%, transparent 100%),
    radial-gradient(1px 1px at 78% 85%, rgba(255,255,255,0.40) 0%, transparent 100%),
    radial-gradient(1px 1px at 91% 14%, rgba(255,255,255,0.30) 0%, transparent 100%),
    radial-gradient(1px 1px at 22% 54%, rgba(255,255,255,0.25) 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 67% 63%, rgba(240,169,50,0.35) 0%, transparent 100%),
    radial-gradient(1px 1px at 45% 92%, rgba(255,255,255,0.20) 0%, transparent 100%),
    radial-gradient(1px 1px at 3%  44%, rgba(255,255,255,0.28) 0%, transparent 100%),
    radial-gradient(1px 1px at 88% 52%, rgba(0,212,255,0.25) 0%, transparent 100%);
  pointer-events: none;
  z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox select {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
}

/* ── Main block ── */
[data-testid="stMain"] { background: transparent !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1100px !important; }

/* ── Typography ── */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; color: #fff !important; }

/* ── Inputs ── */
.stTextInput input, textarea {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: #fff !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.9rem !important;
  padding: 0.8rem 1rem !important;
  transition: border-color 0.25s;
}
.stTextInput input:focus, textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px rgba(0,212,255,0.12) !important;
  outline: none !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--cyan) 0%, #006dff 100%) !important;
  border: none !important;
  border-radius: var(--radius) !important;
  color: #050a18 !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  letter-spacing: 0.05em !important;
  padding: 0.7rem 2rem !important;
  cursor: pointer !important;
  transition: opacity 0.2s, transform 0.15s !important;
  width: 100% !important;
}
.stButton > button:hover  { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button:disabled {
  background: var(--surface2) !important;
  color: var(--text-dim) !important;
  cursor: not-allowed !important;
  transform: none !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
  background: transparent !important;
  border: 1px solid var(--cyan) !important;
  color: var(--cyan) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: var(--cyan-dim) !important;
  transform: translateY(-1px) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--cyan) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
}
.streamlit-expanderContent {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius) var(--radius) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
  color: var(--cyan) !important;
  font-family: 'JetBrains Mono', monospace !important;
}

/* ── Alerts / info ── */
.stAlert {
  background: var(--surface) !important;
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.82rem !important;
}
.stAlert.info  { border-left: 3px solid var(--cyan)  !important; }
.stAlert.error { border-left: 3px solid var(--error) !important; }

/* ── Markdown ── */
.element-container p, .stMarkdown p { 
  color: var(--text) !important; 
  line-height: 1.75 !important;
  font-family: 'Lora', Georgia, serif !important;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: 'Syne', sans-serif !important;
  color: #fff !important;
}
.stMarkdown a { color: var(--cyan) !important; }
.stMarkdown code {
  background: var(--surface2) !important;
  color: var(--gold) !important;
  font-family: 'JetBrains Mono', monospace !important;
  border-radius: 4px !important;
  padding: 0.1em 0.35em !important;
}
.stMarkdown pre {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 2rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--surface2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--border); }

/* ── Selectbox ── */
.stSelectbox > div > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Load environment variables ─────────────────────────────────────────────────
load_dotenv(override=True)
gemini_api_key    = os.getenv("GEMINI_API_KEY", "")
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "")
st.session_state.gemini_api_key    = gemini_api_key
st.session_state.firecrawl_api_key = firecrawl_api_key


# ── Helper: render a styled card ───────────────────────────────────────────────
def card(html: str, accent: str = "#00d4ff"):
    st.markdown(
        f"""<div style="
          background: #0d1230;
          border: 1px solid {accent}30;
          border-left: 3px solid {accent};
          border-radius: 12px;
          padding: 1.25rem 1.5rem;
          margin: 0.6rem 0;
          font-family: 'Lora', Georgia, serif;
          color: #c8d8f0;
          line-height: 1.7;
        ">{html}</div>""",
        unsafe_allow_html=True,
    )


def step_badge(n: int, label: str, status: str = "idle"):
    """Render a step badge. status: idle | active | done | error"""
    colors = {
        "idle":   ("#6a7fa8", "#111840"),
        "active": ("#00d4ff", "#0d1a30"),
        "done":   ("#00e5a0", "#0d2420"),
        "error":  ("#ff5757", "#2a0d0d"),
    }
    text_col, bg = colors.get(status, colors["idle"])
    icon = {"idle": "○", "active": "◉", "done": "✓", "error": "✗"}.get(status, "○")
    st.markdown(
        f"""<div style="
          display:flex; align-items:center; gap:0.75rem;
          background:{bg}; border:1px solid {text_col}35;
          border-radius:10px; padding:0.6rem 1rem; margin:0.4rem 0;
          font-family:'Syne',sans-serif;
        ">
          <span style="font-size:1.1rem;color:{text_col};">{icon}</span>
          <span style="font-size:0.78rem;font-family:'JetBrains Mono',monospace;
                       color:{text_col};letter-spacing:.06em;">STEP {n}</span>
          <span style="font-size:0.95rem;font-weight:600;color:{text_col};">{label}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def source_card(url: str, title: str, index: int):
    domain = url.split("/")[2] if "://" in url else url[:30]
    st.markdown(
        f"""<div style="
          background:#0d1230; border:1px solid rgba(0,212,255,0.15);
          border-radius:10px; padding:0.8rem 1.1rem; margin:0.4rem 0;
          display:flex; align-items:flex-start; gap:0.9rem;
        ">
          <span style="
            background:rgba(0,212,255,0.12); color:#00d4ff;
            font-family:'Syne',sans-serif; font-weight:700;
            font-size:0.75rem; padding:0.3rem 0.55rem;
            border-radius:6px; min-width:28px; text-align:center; margin-top:2px;
          ">{index:02d}</span>
          <div>
            <div style="color:#e8f0ff;font-family:'Syne',sans-serif;font-weight:600;
                        font-size:0.9rem;margin-bottom:0.2rem;">
              {title or "Untitled Source"}
            </div>
            <a href="{url}" target="_blank" style="
              color:#6a9fd8;font-family:'JetBrains Mono',monospace;
              font-size:0.75rem;text-decoration:none;word-break:break-all;
            ">{domain}…</a>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem;">
      <div style="font-size:2.5rem;">🔭</div>
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.2rem;
                  color:#00d4ff;letter-spacing:0.08em;">DEEP RESEARCH</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                  color:#6a7fa8;letter-spacing:0.15em;margin-top:0.2rem;">AGENT v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""<div style="font-family:'Syne',sans-serif;font-weight:700;
                               font-size:0.8rem;color:#6a7fa8;letter-spacing:0.1em;
                               margin-bottom:0.5rem;">⚙ RESEARCH SETTINGS</div>""",
                unsafe_allow_html=True)

    max_depth = st.selectbox("Crawl Depth", [1, 2, 3, 4, 5], index=2,
                             help="Higher depth = more thorough but slower")
    time_limit = st.selectbox("Time Limit (s)", [60, 120, 180, 300], index=2)
    max_urls   = st.selectbox("Max URLs", [5, 10, 15, 20], index=1)

    st.markdown("---")

    st.markdown("""<div style="font-family:'Syne',sans-serif;font-weight:700;
                               font-size:0.8rem;color:#6a7fa8;letter-spacing:0.1em;
                               margin-bottom:0.5rem;">ℹ HOW IT WORKS</div>""",
                unsafe_allow_html=True)

    for step_text in [
        "🌐  Firecrawl deep-searches the web",
        "🧠  Gemini synthesizes an initial report",
        "✨  Gemini enhances with deeper insights",
    ]:
        card(f"<span style='font-size:0.85rem;'>{step_text}</span>", accent="#006dff")

    st.markdown("---")
    st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                               color:#6a7fa8;text-align:center;">
      Powered by Gemini 2.5 Flash &amp; Firecrawl
    </div>""", unsafe_allow_html=True)


# ── Main header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2.5rem;">
  <div style="
    font-family:'Syne',sans-serif;font-weight:800;font-size:2.6rem;
    color:#fff;letter-spacing:-0.02em;line-height:1.1;
    background:linear-gradient(135deg,#fff 30%,#00d4ff 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  ">Deep Research Agent</div>
  <div style="
    font-family:'Lora',Georgia,serif;font-style:italic;
    color:#6a7fa8;font-size:1.05rem;margin-top:0.5rem;
  ">Multi-step intelligence — from the open web to actionable insight</div>
</div>
""", unsafe_allow_html=True)


# ── API key warnings ───────────────────────────────────────────────────────────
missing = []
if not gemini_api_key:    missing.append("GEMINI_API_KEY")
if not firecrawl_api_key: missing.append("FIRECRAWL_API_KEY")
if missing:
    st.error(f"⚠ Missing API keys in `.env`: {', '.join(missing)}")


# ── Research input ─────────────────────────────────────────────────────────────
st.markdown("""<div style="font-family:'Syne',sans-serif;font-weight:600;
                           font-size:0.85rem;color:#6a7fa8;letter-spacing:0.08em;
                           margin-bottom:0.4rem;">RESEARCH TOPIC</div>""",
            unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1], gap="medium")
with col_input:
    research_topic = st.text_input(
        label="topic",
        placeholder="e.g.  Latest breakthroughs in solid-state batteries",
        label_visibility="collapsed",
    )
with col_btn:
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    start = st.button("🔭  Research", disabled=not research_topic or bool(missing))


# ── Example chips ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin:0.8rem 0 2rem;">
  <span style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
               color:#6a7fa8;align-self:center;">Try:</span>
  {chips}
</div>
""".format(chips="".join([
    f"""<span style="background:#111840;border:1px solid rgba(0,212,255,0.2);
        color:#8ab4d4;font-family:'JetBrains Mono',monospace;font-size:0.72rem;
        padding:0.25rem 0.65rem;border-radius:20px;">{t}</span>"""
    for t in [
        "Quantum computing 2025",
        "LLM reasoning techniques",
        "Climate tipping points",
        "CRISPR gene editing ethics",
        "Space tourism economics",
    ]
])),
    unsafe_allow_html=True,
)


# ── Research pipeline ──────────────────────────────────────────────────────────
async def run_research_process(topic: str):
    client = genai.Client(api_key=st.session_state.gemini_api_key)

    # ── Step status placeholders ───────────────────────────────────────────────
    step_col1, step_col2, step_col3 = st.columns(3)

    with step_col1:
        s1 = st.empty()
        s1.markdown(render_step(1, "Web Research",   "active"), unsafe_allow_html=True)
    with step_col2:
        s2 = st.empty()
        s2.markdown(render_step(2, "Synthesis",      "idle"),   unsafe_allow_html=True)
    with step_col3:
        s3 = st.empty()
        s3.markdown(render_step(3, "Enhancement",    "idle"),   unsafe_allow_html=True)

    activity = st.empty()
    progress  = st.progress(0, text="Initializing…")

    # ── STEP 1: Firecrawl ──────────────────────────────────────────────────────
    headers = {
        "Authorization": f"Bearer {st.session_state.firecrawl_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": topic,
        "maxDepth": max_depth,
        "timeLimit": time_limit,
        "maxUrls": max_urls,
    }

    try:
        activity.info("⬡ Starting Firecrawl deep research job…")
        resp = requests.post("https://api.firecrawl.dev/v1/deep-research",
                             headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        job_id = resp.json().get("id")
        if not job_id:
            raise ValueError(f"No job ID returned: {resp.json()}")

        poll_count = 0
        while True:
            time.sleep(5)
            poll_count += 1
            pct = min(poll_count * 4, 33)
            progress.progress(pct, text=f"🔍 Crawling the web… ({poll_count * 5}s elapsed)")
            activity.info(f"⬡ Polling job `{job_id}` — attempt {poll_count}")

            sr = requests.get(f"https://api.firecrawl.dev/v1/deep-research/{job_id}",
                              headers=headers, timeout=60)
            sd = sr.json()
            status = sd.get("status", "unknown")

            if status == "completed":
                activity.empty()
                break
            if status == "failed":
                raise RuntimeError(f"Firecrawl job failed: {sd}")

        data = sd.get("data", {})
        inner = data.get("data", data)
        final_analysis = inner.get("finalAnalysis", "No analysis returned.")
        sources = inner.get("sources", [])
        sources_text = "\n".join(
            [f"- {s.get('url','')} (Title: {s.get('title','Untitled')})" for s in sources]
        )
        research_context = f"Final Analysis:\n{final_analysis}\n\nSources:\n{sources_text}"

        s1.markdown(render_step(1, "Web Research", "done"), unsafe_allow_html=True)
        progress.progress(34, text="✓ Web research complete")

        # Show sources
        if sources:
            with st.expander(f"📎 {len(sources)} Sources Discovered", expanded=False):
                for i, s in enumerate(sources, 1):
                    source_card(s.get("url", "#"), s.get("title", ""), i)

    except Exception as e:
        s1.markdown(render_step(1, "Web Research", "error"), unsafe_allow_html=True)
        progress.progress(100, text="❌ Error in Step 1")
        activity.empty()
        st.error(f"Firecrawl error: {e}")
        return None

    # ── STEP 2: Synthesis ──────────────────────────────────────────────────────
    s2.markdown(render_step(2, "Synthesis", "active"), unsafe_allow_html=True)
    progress.progress(40, text="🧠 Synthesizing report with Gemini…")
    activity.info("⬡ Sending research context to Gemini 2.5 Flash…")

    synthesis_prompt = f"""You are an expert research analyst. 
Based on the following deep research context about: "{topic}", 
write a comprehensive, well-structured research report.

Requirements:
- Use clear headings and subheadings
- Include key findings, data points, and insights
- Cite sources where applicable
- Maintain academic rigor and factual accuracy
- Structure: Executive Summary → Key Findings → Detailed Analysis → Implications

Research Context:
{research_context}
"""
    try:
        r2 = client.models.generate_content(model="gemini-2.5-flash", contents=synthesis_prompt)
        initial_report = r2.text
    except Exception as e:
        s2.markdown(render_step(2, "Synthesis", "error"), unsafe_allow_html=True)
        st.error(f"Gemini synthesis error: {e}")
        return None

    s2.markdown(render_step(2, "Synthesis", "done"), unsafe_allow_html=True)
    progress.progress(67, text="✓ Initial report synthesized")
    activity.empty()

    with st.expander("📄 Initial Research Report (pre-enhancement)", expanded=False):
        st.markdown(initial_report)

    # ── STEP 3: Enhancement ────────────────────────────────────────────────────
    s3.markdown(render_step(3, "Enhancement", "active"), unsafe_allow_html=True)
    progress.progress(70, text="✨ Enhancing with deeper insights…")
    activity.info("⬡ Running elaboration pass with Gemini 2.5 Flash…")

    elaboration_prompt = f"""You are an expert content enhancer specialising in research synthesis.

RESEARCH TOPIC: {topic}

INITIAL REPORT:
{initial_report}

Enhance this report:
- Deepen explanations of complex concepts with clear examples
- Add real-world case studies and practical applications
- Expand key points with additional context and nuance
- Add a "Future Outlook" section with predictions and implications
- Add a "Key Takeaways" bullet summary at the very top
- Maintain all source citations from the original
- Keep the enhanced report engaging, rigorous, and comprehensive
"""
    try:
        r3 = client.models.generate_content(model="gemini-2.5-flash", contents=elaboration_prompt)
        enhanced = r3.text
    except Exception as e:
        s3.markdown(render_step(3, "Enhancement", "error"), unsafe_allow_html=True)
        st.error(f"Gemini enhancement error: {e}")
        return initial_report  # fall back gracefully

    s3.markdown(render_step(3, "Enhancement", "done"), unsafe_allow_html=True)
    progress.progress(100, text="✅ Research complete!")
    activity.empty()

    return enhanced, sources


def render_step(n: int, label: str, status: str) -> str:
    colors = {
        "idle":   ("#6a7fa8", "#111840", "○"),
        "active": ("#00d4ff", "#0d1a30", "◉"),
        "done":   ("#00e5a0", "#0d2420", "✓"),
        "error":  ("#ff5757", "#2a0d0d", "✗"),
    }
    c, bg, icon = colors.get(status, colors["idle"])
    pulse = "animation:pulse 1.2s ease-in-out infinite;" if status == "active" else ""
    return f"""
<style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.45}}}}</style>
<div style="background:{bg};border:1px solid {c}35;border-radius:10px;
            padding:0.75rem 1rem;text-align:center;{pulse}">
  <div style="font-size:1.3rem;color:{c};">{icon}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
              color:{c};letter-spacing:.1em;margin:0.2rem 0;">STEP {n}</div>
  <div style="font-family:'Syne',sans-serif;font-weight:700;
              font-size:0.85rem;color:{c};">{label}</div>
</div>"""


# ── Trigger research ───────────────────────────────────────────────────────────
if start and research_topic:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                  color:#6a7fa8;letter-spacing:0.1em;">RESEARCHING</div>
      <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.4rem;
                  color:#fff;margin-top:0.2rem;">"{research_topic}"</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        result = asyncio.run(run_research_process(research_topic))

        if result:
            enhanced_report, sources = result if isinstance(result, tuple) else (result, [])

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.6rem;
                        color:#fff;margin-bottom:0.5rem;">
              ✨ Enhanced Research Report
            </div>
            <div style="font-family:'Lora',serif;font-style:italic;color:#6a7fa8;
                        margin-bottom:1.5rem;font-size:0.95rem;">
              Synthesized and enhanced by Gemini 2.5 Flash
            </div>
            """, unsafe_allow_html=True)

            # Report display in a styled container
            st.markdown(
                f"""<div style="
                  background:#0d1230;border:1px solid rgba(0,212,255,0.18);
                  border-radius:14px;padding:2rem 2.5rem;line-height:1.8;
                ">""",
                unsafe_allow_html=True,
            )
            st.markdown(enhanced_report)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            dc1, dc2, _ = st.columns([1, 1, 2])
            with dc1:
                st.download_button(
                    "⬇ Download .md",
                    enhanced_report,
                    file_name=f"{research_topic[:40].replace(' ','_')}_report.md",
                    mime="text/markdown",
                )
            with dc2:
                html_report = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Research: {research_topic}</title>
<style>
body{{font-family:Georgia,serif;max-width:860px;margin:3rem auto;
     padding:0 1.5rem;color:#222;line-height:1.75;background:#fefefe}}
h1,h2,h3{{font-family:sans-serif;color:#111}}
a{{color:#0070cc}}code{{background:#f3f3f3;padding:.1em .35em;border-radius:3px}}
</style></head><body>
<h1>Deep Research Report</h1>
<p><strong>Topic:</strong> {research_topic}</p>
<hr>
{enhanced_report.replace(chr(10), '<br>')}
</body></html>"""
                st.download_button(
                    "⬇ Download .html",
                    html_report,
                    file_name=f"{research_topic[:40].replace(' ','_')}_report.html",
                    mime="text/html",
                )

    except Exception as e:
        st.error(f"Unexpected error: {e}")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  text-align:center;margin-top:4rem;padding-top:1.5rem;
  border-top:1px solid rgba(0,212,255,0.1);
  font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#4a5878;
">
  Deep Research Agent &nbsp;·&nbsp; Gemini 2.5 Flash &nbsp;·&nbsp; Firecrawl
  &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)
