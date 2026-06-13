import streamlit as st
import streamlit.components.v1 as components
import time
import logging
import traceback
import sys
import os
from pathlib import Path
from datetime import datetime

# ─── LOGGING SETUP ────────────────────────────────────────────────────────────
LOG_DIR = Path("/tmp/deep_research_logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("deep_research")
log.info("=" * 60)
log.info("App started — log file: %s", LOG_FILE)

# ─── SAFE IMPORTS ─────────────────────────────────────────────────────────────
try:
    from graph.workflow import app as workflow_app
    log.info("workflow imported successfully")
    WORKFLOW_OK = True
except Exception as e:
    log.error("Failed to import workflow: %s", e)
    log.debug(traceback.format_exc())
    WORKFLOW_OK = False

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    log.info("reportlab imported successfully")
    REPORTLAB_OK = True
except Exception as e:
    log.error("Failed to import reportlab: %s", e)
    REPORTLAB_OK = False

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Deep Research AI",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed",
)
log.debug("Page config set")

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0c0e14 !important; }
[data-testid="stSidebar"]           { display: none !important; }
#MainMenu, footer, header           { visibility: hidden !important; }
.block-container                    { padding: 1rem 0 0 0 !important; max-width: 100% !important; }
div[data-testid="stVerticalBlock"]  { gap: 0 !important; }
div[data-testid="column"]           { padding: 0 !important; }
.stTextInput > div > div > input {
    background: #10121a !important;
    border: 1px solid #1e2130 !important;
    border-radius: 10px !important;
    color: #c8ccdf !important;
    font-size: 14px !important;
    padding: 10px 16px !important;
    height: 44px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2e2a50 !important;
    box-shadow: none !important;
}
.stTextInput > label { display: none !important; }
.stButton > button {
    background: #8b7cf8 !important;
    border: none !important;
    color: #fff !important;
    border-radius: 10px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    height: 44px !important;
    width: 44px !important;
    padding: 0 !important;
    line-height: 1 !important;
}
.stButton > button:hover { background: #7c6ef0 !important; }
.stDownloadButton > button {
    background: #1e1a36 !important;
    border: 1px solid #2e2a50 !important;
    color: #8b7cf8 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    padding: 6px 14px !important;
}
.stSpinner > div { color: #8b7cf8 !important; }
.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "messages":     [],
    "history":      [],
    "pdf_paths":    {},
    "agent_states": {
        "planner":    {"label": "Planner",    "icon": "🗺",  "cls": "purple", "state": "idle", "detail": "Waiting…"},
        "researcher": {"label": "Researcher", "icon": "🔍", "cls": "teal",   "state": "idle", "detail": "Waiting…"},
        "writer":     {"label": "Writer",     "icon": "✏",  "cls": "coral",  "state": "idle", "detail": "Waiting…"},
        "critic":     {"label": "Critic",     "icon": "🛡",  "cls": "blue",   "state": "idle", "detail": "Waiting…"},
    },
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v
        log.debug("Session state initialised: %s", k)

# ─── PDF GENERATION ───────────────────────────────────────────────────────────
def generate_pdf(text: str, query: str) -> str | None:
    if not REPORTLAB_OK:
        log.error("generate_pdf called but reportlab is not available")
        return None

    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in query[:40])
    path = str(LOG_DIR / f"report_{safe_name}_{datetime.now().strftime('%H%M%S')}.pdf")
    log.info("Generating PDF → %s", path)

    try:
        doc = SimpleDocTemplate(
            path,
            leftMargin=20*mm, rightMargin=20*mm,
            topMargin=20*mm,  bottomMargin=20*mm,
        )
        styles    = getSampleStyleSheet()
        body_styl = ParagraphStyle("body", parent=styles["Normal"], fontSize=11, leading=17)
        content   = []
        for para in text.split("\n"):
            stripped = para.strip()
            if stripped:
                content.append(Paragraph(stripped, body_styl))
                content.append(Spacer(1, 6))

        doc.build(content)
        size_kb = Path(path).stat().st_size // 1024
        log.info("PDF generated OK — %d KB", size_kb)
        return path

    except Exception as e:
        log.error("PDF generation failed: %s", e)
        log.debug(traceback.format_exc())
        return None

# ─── AGENT STATE HELPER ───────────────────────────────────────────────────────
def set_agent(key: str, state: str, detail: str) -> None:
    st.session_state.agent_states[key]["state"]  = state
    st.session_state.agent_states[key]["detail"] = detail
    log.info("Agent %-12s → %-8s | %s", key, state, detail)

# ─── HTML BUILDERS ────────────────────────────────────────────────────────────
def build_sidebar_html() -> str:
    log.debug("Building sidebar HTML")
    agents      = st.session_state.agent_states
    agent_order = ["planner", "researcher", "writer", "critic"]

    nodes = ""
    for i, key in enumerate(agent_order):
        a      = agents[key]
        is_done = a["state"] == "done"
        cls    = "done" if is_done else "idle"
        check  = '<span class="a-check">✓</span>' if is_done else ""
        nodes += f"""
        <div class="agent-node {cls}">
            <div class="a-icon {a['cls']}">{a['icon']}</div>
            <div class="a-text">
                <p class="a-name">{a['label']}</p>
                <p class="a-state">{a['detail']}</p>
            </div>
            {check}
        </div>
        """
        if i < len(agent_order) - 1:
            nodes += '<div class="connector"></div>'

    history_items = ""
    for item in st.session_state.history[-5:][::-1]:
        label = item[:28] + "…" if len(item) > 28 else item
        history_items += f'<div class="hist-item">📄 {label}</div>'

    hist_section = f"""
    <div class="hist-wrap">
        <div class="sec-label" style="padding:0 0 8px;">Recent</div>
        {history_items}
    </div>
    """ if history_items else ""

    return f"""
    <div class="sidebar">
        <div class="logo-block">
            <div class="logo-icon">🔭</div>
            <div>
                <p class="logo-name">Deep Research</p>
                <p class="logo-sub">Multi-agent AI</p>
            </div>
        </div>
        <div class="sec-label">Agent pipeline</div>
        <div class="agent-list">{nodes}</div>
        {hist_section}
    </div>
    """


def build_messages_html() -> str:
    log.debug("Building messages HTML — %d messages", len(st.session_state.messages))
    if not st.session_state.messages:
        return """
        <div class="empty-state">
            <div class="empty-icon">🔭</div>
            <p class="empty-title">Ready to research</p>
            <p class="empty-sub">Type a topic below and the agent pipeline will generate a full report</p>
        </div>
        """

    html = ""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            html += f'<div class="user-bubble">{msg["content"]}</div>'
        else:
            r              = msg["result"]
            report_preview = r.get("report",   "")[:700] + ("…" if len(r.get("report",""))   > 700 else "")
            plan_preview   = r.get("plan",     "")[:160] + ("…" if len(r.get("plan",""))     > 160 else "")
            crit_preview   = r.get("critique", "")[:160] + ("…" if len(r.get("critique","")) > 160 else "")
            html += f"""
            <div class="report-card">
                <div class="iter-trail">
                    <span class="iter-step">🗺 plan</span>
                    <span class="iter-sep">›</span>
                    <span class="iter-step">🔍 research</span>
                    <span class="iter-sep">›</span>
                    <span class="iter-step">✏ write</span>
                    <span class="iter-sep">›</span>
                    <span class="iter-step">🛡 critique</span>
                </div>
                <span class="report-tag">FINAL REPORT</span>
                <div class="report-title">{msg["content"]}</div>
                <div class="report-body">{report_preview}</div>
                <div class="meta-grid">
                    <div class="meta-box">
                        <div class="meta-lbl">🗺 Plan</div>
                        <div class="meta-val">{plan_preview}</div>
                    </div>
                    <div class="meta-box">
                        <div class="meta-lbl">🛡 Critique</div>
                        <div class="meta-val">{crit_preview}</div>
                    </div>
                </div>
            </div>
            """
    return html

# ─── RENDER LAYOUT ────────────────────────────────────────────────────────────
done_count    = sum(1 for a in st.session_state.agent_states.values() if a["state"] == "done")
sidebar_html  = build_sidebar_html()
messages_html = build_messages_html()
log.debug("Rendering layout — %d agents done", done_count)

full_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
.layout {{ display: grid; grid-template-columns: 210px 1fr; height: 560px; border: 1px solid #1e2130; border-radius: 12px; overflow: hidden; background: #0c0e14; }}
.sidebar {{ background: #10121a; border-right: 1px solid #1e2130; display: flex; flex-direction: column; overflow: hidden; }}
.logo-block {{ display: flex; align-items: center; gap: 10px; padding: 18px 14px 14px; border-bottom: 1px solid #1e2130; flex-shrink: 0; }}
.logo-icon {{ width: 32px; height: 32px; background: #161924; border: 1px solid #2a2d3e; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; }}
.logo-name {{ font-size: 13px; font-weight: 600; color: #e2e4f0; }}
.logo-sub  {{ font-size: 10px; color: #5a5f7a; margin-top: 1px; }}
.sec-label {{ font-size: 9px; font-weight: 700; letter-spacing: .09em; color: #3e4260; text-transform: uppercase; padding: 14px 14px 7px; flex-shrink: 0; }}
.agent-list {{ padding: 0 8px; flex-shrink: 0; }}
.agent-node {{ display: flex; align-items: center; gap: 8px; padding: 8px 8px; border-radius: 8px; border: 1px solid transparent; margin-bottom: 1px; }}
.agent-node.done {{ background: #161924; border-color: #1e2130; }}
.agent-node.idle {{ opacity: .35; }}
.a-icon {{ width: 26px; height: 26px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; }}
.a-icon.purple {{ background: #1e1a36; }} .a-icon.teal {{ background: #0d2220; }} .a-icon.coral {{ background: #261510; }} .a-icon.blue {{ background: #0d1a2e; }}
.a-text {{ flex: 1; min-width: 0; }}
.a-name  {{ font-size: 11px; font-weight: 500; color: #c8ccdf; }}
.a-state {{ font-size: 9px; color: #5a5f7a; margin-top: 1px; }}
.a-check {{ font-size: 11px; color: #1fc99a; margin-left: auto; flex-shrink: 0; }}
.connector {{ width: 1px; height: 8px; background: #1e2130; margin: 0 auto 0 20px; }}
.hist-wrap {{ border-top: 1px solid #1e2130; padding: 10px 8px 8px; margin-top: auto; }}
.hist-item {{ display: flex; align-items: center; gap: 5px; padding: 5px 6px; border-radius: 6px; font-size: 10px; color: #5a5f7a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 1px; }}
.main-col {{ display: flex; flex-direction: column; overflow: hidden; background: #0c0e14; }}
.topbar {{ display: flex; align-items: center; gap: 8px; padding: 12px 20px; border-bottom: 1px solid #1e2130; flex-shrink: 0; background: #0c0e14; }}
.topbar-title {{ font-size: 14px; font-weight: 600; color: #e2e4f0; flex: 1; }}
.badge {{ display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 20px; border: 1px solid #1e2130; font-size: 10px; color: #5a5f7a; background: #10121a; }}
.dot-green {{ width:5px; height:5px; border-radius:50%; background:#1fc99a; display:inline-block; }}
.messages {{ flex: 1; padding: 16px 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }}
.empty-state {{ margin: auto; text-align: center; padding: 20px; }}
.empty-icon  {{ font-size: 36px; margin-bottom: 10px; }}
.empty-title {{ font-size: 15px; font-weight: 600; color: #c8ccdf; margin-bottom: 6px; }}
.empty-sub   {{ font-size: 12px; color: #5a5f7a; line-height: 1.6; max-width: 260px; margin: 0 auto; }}
.user-bubble {{ align-self: flex-end; max-width: 65%; background: #161924; border: 1px solid #1e2130; border-radius: 14px 4px 14px 14px; padding: 9px 14px; font-size: 13px; color: #c8ccdf; line-height: 1.5; }}
.report-card {{ background: #10121a; border: 1px solid #1e2130; border-radius: 12px; padding: 14px 18px; }}
.iter-trail {{ display: flex; align-items: center; gap: 5px; margin-bottom: 10px; }}
.iter-step  {{ font-size: 9px; color: #1fc99a; }}
.iter-sep   {{ font-size: 9px; color: #2a2d3e; }}
.report-tag {{ display: inline-block; font-size: 9px; font-weight: 700; letter-spacing: .07em; padding: 3px 8px; border-radius: 20px; background: #1e1a36; color: #8b7cf8; margin-bottom: 8px; }}
.report-title {{ font-size: 14px; font-weight: 600; color: #e2e4f0; margin-bottom: 8px; }}
.report-body  {{ font-size: 12px; color: #7a7f9a; line-height: 1.7; }}
.meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-top: 12px; }}
.meta-box {{ background: #0c0e14; border: 1px solid #1e2130; border-radius: 7px; padding: 9px 11px; }}
.meta-lbl {{ font-size: 9px; font-weight: 700; letter-spacing: .07em; color: #3e4260; text-transform: uppercase; margin-bottom: 4px; }}
.meta-val {{ font-size: 10px; color: #5a5f7a; line-height: 1.6; }}
</style>
</head>
<body style="background:#0c0e14;">
<div class="layout">
    {sidebar_html}
    <div class="main-col">
        <div class="topbar">
            <span class="topbar-title">Research session</span>
            <span class="badge"><span class="dot-green"></span> {done_count} agents done</span>
            <span class="badge">🔁 max 2 iterations</span>
        </div>
        <div class="messages" id="msgs">{messages_html}</div>
    </div>
</div>
<script>
const msgs = document.getElementById('msgs');
if (msgs) msgs.scrollTop = msgs.scrollHeight;
</script>
</body>
</html>
"""

components.html(full_html, height=580, scrolling=False)

# ─── IMPORT WARNING ───────────────────────────────────────────────────────────
if not WORKFLOW_OK:
    st.error("⚠️ Could not load `graph.workflow` — check the terminal logs for details.")
if not REPORTLAB_OK:
    st.warning("⚠️ `reportlab` not found — PDF export will be disabled.")

# ─── PERSISTENT PDF DOWNLOAD BUTTONS ─────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        key = msg["content"][:30]
        pdf = st.session_state.pdf_paths.get(key)
        if pdf and Path(pdf).exists():
            label = msg["content"][:45] + ("…" if len(msg["content"]) > 45 else "")
            try:
                with open(pdf, "rb") as f:
                    st.download_button(
                        f"📄 Download report — {label}",
                        f,
                        file_name="deep_research_report.pdf",
                        mime="application/pdf",
                        key=f"dl_{key}",
                    )
                log.debug("Rendered download button for: %s", key)
            except Exception as e:
                log.error("Could not render download button for '%s': %s", key, e)
        elif pdf:
            log.warning("PDF file missing from disk: %s", pdf)

# ─── INPUT ROW ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
col_input, col_btn = st.columns([11, 1])
with col_input:
    query = st.text_input(
        "q",
        placeholder="New research topic… e.g. Transformer architectures",
        label_visibility="collapsed",
        key="query_input",
    )
with col_btn:
    run = st.button("↑", use_container_width=True)

# ─── DEBUG PANEL (sidebar toggle) ─────────────────────────────────────────────
with st.expander("🛠 Debug / Logs", expanded=False):
    st.caption(f"Log file: `{LOG_FILE}`")
    st.caption(f"Workflow loaded: `{WORKFLOW_OK}` | ReportLab: `{REPORTLAB_OK}`")
    st.caption(f"Messages: {len(st.session_state.messages)} | PDFs saved: {len(st.session_state.pdf_paths)}")
    if st.button("📋 Show last 40 log lines"):
        try:
            lines = LOG_FILE.read_text(encoding="utf-8").splitlines()[-40:]
            st.code("\n".join(lines), language="text")
        except Exception as e:
            st.error(f"Could not read log: {e}")
    if st.button("🗑 Clear session"):
        log.info("Session cleared by user")
        for k in DEFAULTS:
            st.session_state[k] = DEFAULTS[k] if not isinstance(DEFAULTS[k], dict) else dict(DEFAULTS[k])
        st.rerun()

# ─── PIPELINE RUN ─────────────────────────────────────────────────────────────
if run and query:
    if not WORKFLOW_OK:
        st.error("Cannot run — workflow failed to load. See debug panel.")
        log.error("Run attempted but workflow not available")
        st.stop()

    log.info("New query received: '%s'", query)
    st.session_state.history.append(query)
    st.session_state.messages.append({"role": "user", "content": query})

    progress = st.progress(0, text="🗺 Planner thinking…")
    t_start  = time.perf_counter()

    try:
        with st.spinner("Agents working…"):

            # ── Planner ──────────────────────────────────────────────────────
            t0 = time.perf_counter()
            set_agent("planner", "done", "Outline ready")
            progress.progress(20, text="🔍 Researcher collecting sources…")
            log.debug("Planner step took %.2fs", time.perf_counter() - t0)

            # ── Researcher ────────────────────────────────────────────────────
            t0 = time.perf_counter()
            set_agent("researcher", "done", "Sources collected")
            progress.progress(45, text="✏ Writer drafting…")
            log.debug("Researcher step took %.2fs", time.perf_counter() - t0)

            # ── Writer ────────────────────────────────────────────────────────
            t0 = time.perf_counter()
            set_agent("writer", "done", "Draft complete")
            progress.progress(70, text="🛡 Critic reviewing…")
            log.debug("Writer step took %.2fs", time.perf_counter() - t0)

            # ── Critic ────────────────────────────────────────────────────────
            t0 = time.perf_counter()
            set_agent("critic", "done", "2 revisions applied")
            progress.progress(90, text="⚙ Finalising report…")
            log.debug("Critic step took %.2fs", time.perf_counter() - t0)

            # ── Workflow invoke ───────────────────────────────────────────────
            log.info("Invoking workflow…")
            t0     = time.perf_counter()
            result = workflow_app.invoke({
                "query":          query,
                "iteration":      0,
                "max_iterations": 2,
            })
            elapsed = time.perf_counter() - t0
            log.info("Workflow completed in %.2fs", elapsed)

            # ── Validate result ───────────────────────────────────────────────
            required_keys = {"report", "plan", "critique"}
            missing = required_keys - set(result.keys())
            if missing:
                raise ValueError(f"Workflow result missing keys: {missing}")

            report_len = len(result.get("report", ""))
            log.info(
                "Result sizes — report: %d chars | plan: %d chars | critique: %d chars",
                report_len,
                len(result.get("plan", "")),
                len(result.get("critique", "")),
            )
            if report_len < 50:
                log.warning("Report seems too short (%d chars) — possible truncation", report_len)

        progress.progress(100, text="✓ Done")
        total_elapsed = time.perf_counter() - t_start
        log.info("Pipeline finished in %.2fs total", total_elapsed)

    except Exception as e:
        log.error("Pipeline crashed: %s", e)
        log.debug(traceback.format_exc())
        progress.empty()
        st.error(f"❌ Pipeline error: {e}\n\nCheck the debug panel for full traceback.")
        st.session_state.messages.pop()   # remove orphaned user bubble
        st.session_state.history.pop()
        st.stop()

    progress.empty()

    # ── Save result ───────────────────────────────────────────────────────────
    st.session_state.messages.append({
        "role":    "assistant",
        "content": query,
        "result":  result,
    })

    # ── PDF generation ────────────────────────────────────────────────────────
    pdf_path = generate_pdf(result["report"], query)
    if pdf_path:
        st.session_state.pdf_paths[query[:30]] = pdf_path
        log.info("PDF saved to session state under key: '%s'", query[:30])
    else:
        log.warning("PDF generation returned None — download will not be available")
        if not REPORTLAB_OK:
            st.warning("PDF export skipped — reportlab is not installed.")

    time.sleep(0.3)
    st.rerun()