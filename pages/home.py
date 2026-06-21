from pathlib import Path
import streamlit as st
from utils import styles, content

data = content.load()
site = data.get("site", {})
tasks = data.get("tasks", [])

saved_runs_dir = Path(__file__).parent.parent / "saved_runs"
saved_runs = [d for d in saved_runs_dir.iterdir() if d.is_dir()] if saved_runs_dir.exists() else []

# Hero
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">{site.get('title', 'BRACU DUBURI')}<br>{site.get('subtitle', 'VISION PIPELINE AUTOMATION')}</div>
    <div class="hero-sub">{site.get('tagline', 'Autonomous Underwater Vehicle · Object Detection System')}</div>
    <div class="hero-extra">{site.get('team_name', 'Team BRACU Duburi')} &nbsp;|&nbsp; {site.get('competition', 'RoboSub 2026')}</div>
</div>
""", unsafe_allow_html=True)

# Quick stats
cols = st.columns(4)
with cols[0]: styles.metric_card("Tasks",      str(len(tasks)),        "competition tasks",  "")
with cols[1]: styles.metric_card("Saved Runs", str(len(saved_runs)),   "trained models",     "green")
with cols[2]: styles.metric_card("Workflow Automation", "n8n",         "dataset distribution & collection", "purple")
with cols[3]: styles.metric_card("Competition","2026",                  "RoboSub Irvine, CA", "amber")

st.markdown("<br>", unsafe_allow_html=True)

# Task overview
styles.section("Competition Tasks")

cards_html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px;align-items:stretch">'
for task in tasks:
    color    = task.get("color", "#2563EB")
    run_name = task.get("run_name", "")
    has_run  = (saved_runs_dir / run_name).exists() if run_name else False
    badge = (
        f'<span style="font-size:10px;background:#F0FDF4;color:#059669;'
        f'border:1px solid #BBF7D0;border-radius:20px;padding:2px 8px;font-weight:700">Data ready</span>'
        if has_run else
        f'<span style="font-size:10px;background:#F8FAFC;color:#94A3B8;'
        f'border:1px solid #E2E8F0;border-radius:20px;padding:2px 8px;font-weight:600">Pending</span>'
    )
    cards_html += (
        f'<div style="background:#FFFFFF;border-radius:14px;padding:20px 16px;'
        f'box-shadow:0 2px 16px rgba(13,27,42,0.07);border-top:5px solid {color};'
        f'display:flex;flex-direction:column;justify-content:space-between">'
        f'<div>'
        f'<div style="font-size:15px;font-weight:900;color:{color};margin-bottom:8px">'
        f'{task.get("name","")}</div>'
        f'<div style="font-size:11px;color:#475569;line-height:1.6">'
        f'{task.get("description","")}</div>'
        f'</div>'
        f'<div style="margin-top:12px">{badge}</div>'
        f'</div>'
    )
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

st.divider()

# Vision pipeline — what the system actually does
styles.section("Vision Pipeline")
vision_steps = [
    ("01", "Capture",    "Dive footage recorded during pool trials"),
    ("02", "Annotate",   "Objects labelled per task in CVAT"),
    ("03", "Train",      "YOLO trained on custom underwater data"),
    ("04", "Detect",     "Real-time object detection on the AUV"),
    ("05", "Decide",     "Detections feed the autonomy controller"),
]
v_cols = st.columns(len(vision_steps))
for col, (num, title, desc) in zip(v_cols, vision_steps):
    with col:
        st.markdown(
            f'<div class="step-card">'
            f'<div class="step-num" style="background:#0F172A">{num}</div>'
            f'<div class="step-title">{title}</div>'
            f'<div style="font-size:10px;color:#64748B;line-height:1.5;margin-top:6px">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# Dataset collection pipeline
styles.section("Dataset Collection Pipeline")

col_n8n, col_mid, col_human = st.columns([5, 1, 3], gap="small")

n8n_steps = [
    ("01", "Split Video",   "Dive footage split into labelled clips"),
    ("02", "Distribute",    "Clips sent to annotators via Gmail"),
    ("04", "Collect",       "Annotated zips received and extracted automatically"),
    ("05", "Merge & Train", "Dataset merged, YOLO trained locally"),
]
human_steps = [
    ("Label in CVAT",   "Bounding boxes drawn on each clip per task"),
    ("Export & Reply",  "YOLO format zip exported and sent back via email"),
]

with col_n8n:
    st.markdown(
        '<p style="font-size:10px;font-weight:800;color:#2563EB;text-transform:uppercase;'
        'letter-spacing:3px;margin-bottom:12px">Automated by n8n</p>',
        unsafe_allow_html=True,
    )
    for num, title, desc in n8n_steps:
        st.markdown(
            f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;'
            f'padding:12px 16px;margin-bottom:8px">'
            f'<div style="font-size:11px;font-weight:800;color:#1D4ED8">{num} &nbsp; {title}</div>'
            f'<div style="font-size:11px;color:#64748B;margin-top:3px">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

with col_mid:
    st.markdown(
        '<div style="display:flex;flex-direction:column;align-items:center;'
        'justify-content:center;height:100%;gap:8px;padding-top:32px">'
        '<div style="width:1px;height:40px;background:#E2E8F0"></div>'
        '<div style="background:#F1F5F9;border:1px solid #E2E8F0;border-radius:6px;'
        'padding:6px 8px;font-size:9px;font-weight:800;color:#94A3B8;'
        'text-transform:uppercase;letter-spacing:1px;writing-mode:vertical-rl;'
        'text-orientation:mixed">03</div>'
        '<div style="width:1px;height:40px;background:#E2E8F0"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_human:
    st.markdown(
        '<p style="font-size:10px;font-weight:800;color:#475569;text-transform:uppercase;'
        'letter-spacing:3px;margin-bottom:12px">Human Annotators</p>',
        unsafe_allow_html=True,
    )
    for title, desc in human_steps:
        st.markdown(
            f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;'
            f'padding:12px 16px;margin-bottom:8px">'
            f'<div style="font-size:11px;font-weight:800;color:#334155">{title}</div>'
            f'<div style="font-size:11px;color:#94A3B8;margin-top:3px">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

styles.footer()
