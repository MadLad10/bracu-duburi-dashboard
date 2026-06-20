import streamlit as st
from utils import styles, content, auth

try:
    import requests as _req
except ImportError:
    _req = None

N8N_URL = "http://localhost:5678"

data = content.load()
pipeline = data.get("pipeline", {})

styles.page_header("Automation Pipeline", "Powered by n8n · End-to-End Annotation & Training")

styles.section("How It Works")
st.markdown(
    f'<div class="card" style="margin-bottom:20px">'
    f'<p style="color:#334155;font-size:14px;line-height:1.7">{pipeline.get("description","")}</p>'
    f'</div>',
    unsafe_allow_html=True,
)

styles.section("Pipeline Steps")
STEPS = [
    ("01", "Split Video",   "Raw dive footage split into fixed-length clips for distribution."),
    ("02", "Send Emails",   "n8n sends annotator emails with video clips and task instructions."),
    ("03", "Annotate",      "Annotators label objects in CVAT and export YOLO 1.1 format zips."),
    ("04", "Receive Zips",  "n8n receives reply emails, extracts annotation zips automatically."),
    ("05", "Merge & Split", "All annotations merged and split 85/5/10 train/val/test."),
    ("06", "Train",         "YOLO11n trained on merged dataset with underwater augmentation."),
]

step_cols = st.columns(len(STEPS))
for col, (num, title, desc) in zip(step_cols, STEPS):
    with col:
        st.markdown(
            f'<div class="step-card">'
            f'<div class="step-num">{num}</div>'
            f'<div class="step-title">{title}</div>'
            f'<div style="font-size:10px;color:#64748B;line-height:1.5;margin-top:6px">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
styles.section("n8n Status")

n8n_online = False
if _req:
    try:
        n8n_online = _req.get(f"{N8N_URL}/healthz", timeout=2).ok
    except Exception:
        pass

status_color = "#059669" if n8n_online else "#DC2626"
status_text  = "Online"  if n8n_online else "Offline"
status_bg    = "#F0FDF4" if n8n_online else "#FEF2F2"
status_bdr   = "#BBF7D0" if n8n_online else "#FECACA"

left, right = st.columns([4, 1])
with left:
    st.markdown(
        f'<div style="background:{status_bg};border:1.5px solid {status_bdr};border-radius:12px;'
        f'padding:18px 24px;display:flex;align-items:center;gap:16px">'
        f'<div style="width:12px;height:12px;border-radius:50%;background:{status_color};'
        f'flex-shrink:0;box-shadow:0 0 8px {status_color}88"></div>'
        f'<div><div style="font-size:13px;font-weight:800;color:{status_color}">n8n {status_text}</div>'
        f'<div style="font-size:11px;color:#64748B;margin-top:2px">'
        f'{N8N_URL} &nbsp;|&nbsp; Self-hosted workflow automation</div></div></div>',
        unsafe_allow_html=True,
    )
with right:
    st.link_button("Open n8n Editor", N8N_URL, use_container_width=True)

if n8n_online:
    st.markdown("<br>", unsafe_allow_html=True)
    st.components.v1.iframe(N8N_URL, height=540, scrolling=True)
else:
    st.warning(
        "n8n is not running locally. Start it with `docker run -p 5678:5678 n8nio/n8n` "
        "to see the live workflow editor here.",
    )

styles.footer()
