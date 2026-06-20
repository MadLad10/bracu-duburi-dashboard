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
with cols[2]: styles.metric_card("Annotation", "n8n",                  "workflow automation", "purple")
with cols[3]: styles.metric_card("Competition","2026",                  "RoboSub San Diego",  "amber")

st.markdown("<br>", unsafe_allow_html=True)

# Task overview
styles.section("Competition Tasks")
task_cols = st.columns(len(tasks) if tasks else 1)
for col, task in zip(task_cols, tasks):
    color = task.get("color", "#2563EB")
    run_name = task.get("run_name", "")
    has_run = (saved_runs_dir / run_name).exists() if run_name else False
    badge = (
        f'<span style="font-size:10px;background:#F0FDF4;color:#059669;'
        f'border:1px solid #BBF7D0;border-radius:20px;padding:2px 8px;font-weight:700">Data ready</span>'
        if has_run else
        f'<span style="font-size:10px;background:#F8FAFC;color:#94A3B8;'
        f'border:1px solid #E2E8F0;border-radius:20px;padding:2px 8px;font-weight:600">Pending</span>'
    )
    with col:
        st.markdown(
            f'<div style="background:#FFFFFF;border-radius:14px;padding:20px 16px;'
            f'box-shadow:0 2px 16px rgba(13,27,42,0.07);border-top:5px solid {color}">'
            f'<div style="font-size:18px;font-weight:900;color:{color};margin-bottom:6px">'
            f'{task.get("name","")}</div>'
            f'<div style="font-size:12px;color:#475569;line-height:1.5;margin-bottom:10px">'
            f'{task.get("description","")}</div>'
            f'{badge}</div>',
            unsafe_allow_html=True,
        )

st.divider()

# Vision pipeline — what the system actually does
styles.section("Vision Pipeline")
vision_steps = [
    ("01", "Capture",    "Dive footage recorded during pool trials"),
    ("02", "Annotate",   "Objects labelled per task in CVAT"),
    ("03", "Train",      "YOLO11n trained on custom underwater data"),
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

# Dataset collection pipeline — clearly split what n8n does vs what humans do
styles.section("Dataset Collection Pipeline")
st.markdown(
    '<p style="font-size:12px;color:#64748B;margin:-10px 0 16px 0">'
    'n8n handles <strong>distribution and collection only</strong> — '
    'annotation is done by human annotators in CVAT.</p>',
    unsafe_allow_html=True,
)

# Two groups: n8n-automated steps and manual steps
col_l, col_r = st.columns([3, 2], gap="large")

with col_l:
    st.markdown(
        '<p style="font-size:10px;font-weight:800;color:#2563EB;text-transform:uppercase;'
        'letter-spacing:2px;margin-bottom:10px">Automated by n8n</p>',
        unsafe_allow_html=True,
    )
    n8n_steps = [
        ("01", "Split Video",  "Footage split into clips"),
        ("02", "Send Emails",  "Clips distributed to annotators via Gmail"),
        ("03", "Receive Zips", "Annotated zips collected from replies"),
        ("04", "Merge & Train","Dataset merged, YOLO11n trained locally"),
    ]
    n8n_cols = st.columns(len(n8n_steps))
    for col, (num, title, desc) in zip(n8n_cols, n8n_steps):
        with col:
            st.markdown(
                f'<div class="step-card" style="border-top:3px solid #2563EB">'
                f'<div class="step-num">{num}</div>'
                f'<div class="step-title">{title}</div>'
                f'<div style="font-size:10px;color:#64748B;line-height:1.5;margin-top:6px">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

with col_r:
    st.markdown(
        '<p style="font-size:10px;font-weight:800;color:#475569;text-transform:uppercase;'
        'letter-spacing:2px;margin-bottom:10px">Done by Humans</p>',
        unsafe_allow_html=True,
    )
    human_steps = [
        ("A", "Label in CVAT", "Annotators draw bounding boxes on received clips"),
        ("B", "Export & Reply", "YOLO 1.1 zip exported and sent back via email"),
    ]
    h_cols = st.columns(len(human_steps))
    for col, (num, title, desc) in zip(h_cols, human_steps):
        with col:
            st.markdown(
                f'<div class="step-card" style="border-top:3px solid #94A3B8">'
                f'<div class="step-num" style="background:#475569">{num}</div>'
                f'<div class="step-title">{title}</div>'
                f'<div style="font-size:10px;color:#64748B;line-height:1.5;margin-top:6px">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

styles.footer()
