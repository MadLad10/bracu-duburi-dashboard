import streamlit as st
from pathlib import Path
from utils import styles, content, auth

st.set_page_config(
    page_title="BRACU Duburi — Vision Pipeline",
    page_icon="🤿",
    layout="wide",
    initial_sidebar_state="expanded",
)
styles.inject()

data = content.load()
site = data.get("site", {})
tasks = data.get("tasks", [])

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## BRACU Duburi")
    st.markdown(
        "<p style='color:#60A5FA;font-size:11px;font-weight:600;letter-spacing:2px'>"
        "VISION PIPELINE</p>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        "<p style='color:#94A3B8;font-size:10px;font-weight:700;letter-spacing:1px;"
        "text-transform:uppercase'>Navigation</p>",
        unsafe_allow_html=True,
    )
    st.page_link("dashboard.py",           label="Home",              icon="🏠")
    st.page_link("pages/1_About.py",        label="About Competition", icon="🏆")
    st.page_link("pages/2_Tasks.py",        label="Competition Tasks", icon="🎯")
    st.page_link("pages/3_Pipeline.py",     label="Automation Pipeline", icon="⚙️")
    st.page_link("pages/4_Task_Analytics.py", label="Task Analytics",  icon="📊")
    auth.admin_widget()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">{site.get('title', 'BRACU DUBURI')}<br>{site.get('subtitle', 'VISION PIPELINE AUTOMATION')}</div>
    <div class="hero-sub">{site.get('tagline', 'Autonomous Underwater Vehicle · Object Detection System')}</div>
    <div class="hero-extra">{site.get('team_name', 'Team BRACU Duburi')} &nbsp;|&nbsp; {site.get('competition', 'RoboSub 2026')}</div>
</div>
""", unsafe_allow_html=True)

# ── Quick stats row ───────────────────────────────────────────────────────────
saved_runs_dir = Path(__file__).parent / "saved_runs"
saved_runs = [d for d in saved_runs_dir.iterdir() if d.is_dir()] if saved_runs_dir.exists() else []

cols = st.columns(4)
with cols[0]:
    styles.metric_card("Tasks", str(len(tasks)), "competition tasks", "")
with cols[1]:
    styles.metric_card("Saved Runs", str(len(saved_runs)), "trained models", "green")
with cols[2]:
    styles.metric_card("Pipeline", "n8n", "fully automated", "purple")
with cols[3]:
    styles.metric_card("Competition", "2026", "RoboSub San Diego", "amber")

st.markdown("<br>", unsafe_allow_html=True)

# ── Task overview cards ───────────────────────────────────────────────────────
styles.section("Competition Tasks")
task_cols = st.columns(len(tasks) if tasks else 1)
for col, task in zip(task_cols, tasks):
    color = task.get("color", "#2563EB")
    with col:
        run_name = task.get("run_name", "")
        has_run = (saved_runs_dir / run_name).exists() if run_name else False
        badge = (
            f'<span style="font-size:10px;background:#F0FDF4;color:#059669;'
            f'border:1px solid #BBF7D0;border-radius:20px;padding:2px 8px;font-weight:700">'
            f'✓ Data ready</span>'
            if has_run else
            f'<span style="font-size:10px;background:#F8FAFC;color:#94A3B8;'
            f'border:1px solid #E2E8F0;border-radius:20px;padding:2px 8px;font-weight:600">'
            f'Pending</span>'
        )
        st.markdown(
            f'<div style="background:#FFFFFF;border-radius:14px;padding:20px 16px;'
            f'box-shadow:0 2px 16px rgba(13,27,42,0.07);border-top:5px solid {color};height:100%">'
            f'<div style="font-size:18px;font-weight:900;color:{color};margin-bottom:6px">'
            f'{task.get("name","")}</div>'
            f'<div style="font-size:12px;color:#475569;line-height:1.5;margin-bottom:10px">'
            f'{task.get("description","")}</div>'
            f'{badge}</div>',
            unsafe_allow_html=True,
        )

st.divider()

# ── Pipeline overview ─────────────────────────────────────────────────────────
styles.section("Automation Pipeline")
steps = ["Split Video", "Send Emails", "Annotate", "Receive Zips", "Merge & Split", "Train"]
step_cols = st.columns(len(steps))
for col, (i, name) in zip(step_cols, enumerate(steps, 1)):
    with col:
        st.markdown(
            f'<div class="step-card">'
            f'<div class="step-num">{i:02d}</div>'
            f'<div class="step-title">{name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.info("The entire annotation and training pipeline is automated via **n8n** workflow automation. "
        "Visit the **Automation Pipeline** page for details.", icon="⚙️")

styles.footer()
