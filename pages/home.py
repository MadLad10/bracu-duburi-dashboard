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

st.markdown("""
<div style="background:linear-gradient(135deg,#0D1B2A 0%,#1B3A5C 100%);
            border-radius:16px;padding:32px 36px;margin-bottom:24px">

  <div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:0">

    <!-- n8n automated block -->
    <div>
      <div style="font-size:10px;font-weight:800;color:#60A5FA;text-transform:uppercase;
                  letter-spacing:3px;margin-bottom:18px">Automated by n8n</div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <div style="background:rgba(37,99,235,0.2);border:1px solid rgba(37,99,235,0.4);
                    border-radius:10px;padding:12px 16px">
          <div style="font-size:11px;font-weight:800;color:#93C5FD;letter-spacing:0.5px">01 &nbsp; Split Video</div>
          <div style="font-size:11px;color:#94A3B8;margin-top:3px">Dive footage split into labelled clips</div>
        </div>
        <div style="background:rgba(37,99,235,0.2);border:1px solid rgba(37,99,235,0.4);
                    border-radius:10px;padding:12px 16px">
          <div style="font-size:11px;font-weight:800;color:#93C5FD;letter-spacing:0.5px">02 &nbsp; Distribute</div>
          <div style="font-size:11px;color:#94A3B8;margin-top:3px">Clips sent to annotators via Gmail</div>
        </div>
        <div style="background:rgba(37,99,235,0.2);border:1px solid rgba(37,99,235,0.4);
                    border-radius:10px;padding:12px 16px">
          <div style="font-size:11px;font-weight:800;color:#93C5FD;letter-spacing:0.5px">04 &nbsp; Collect</div>
          <div style="font-size:11px;color:#94A3B8;margin-top:3px">Annotated zips received and extracted automatically</div>
        </div>
        <div style="background:rgba(37,99,235,0.2);border:1px solid rgba(37,99,235,0.4);
                    border-radius:10px;padding:12px 16px">
          <div style="font-size:11px;font-weight:800;color:#93C5FD;letter-spacing:0.5px">05 &nbsp; Merge & Train</div>
          <div style="font-size:11px;color:#94A3B8;margin-top:3px">Dataset merged, YOLO trained locally</div>
        </div>
      </div>
    </div>

    <!-- Divider -->
    <div style="display:flex;flex-direction:column;align-items:center;padding:0 32px;gap:8px">
      <div style="width:1px;height:60px;background:rgba(255,255,255,0.1)"></div>
      <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);
                  border-radius:8px;padding:8px 14px;font-size:10px;font-weight:800;
                  color:#475569;text-transform:uppercase;letter-spacing:2px;white-space:nowrap">
        Step 03
      </div>
      <div style="width:1px;height:60px;background:rgba(255,255,255,0.1)"></div>
    </div>

    <!-- Human block -->
    <div>
      <div style="font-size:10px;font-weight:800;color:#94A3B8;text-transform:uppercase;
                  letter-spacing:3px;margin-bottom:18px">Done by Human Annotators</div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    border-radius:10px;padding:12px 16px">
          <div style="font-size:11px;font-weight:800;color:#CBD5E1;letter-spacing:0.5px">Label in CVAT</div>
          <div style="font-size:11px;color:#64748B;margin-top:3px">Bounding boxes drawn on each clip per task</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    border-radius:10px;padding:12px 16px">
          <div style="font-size:11px;font-weight:800;color:#CBD5E1;letter-spacing:0.5px">Export & Reply</div>
          <div style="font-size:11px;color:#64748B;margin-top:3px">YOLO format zip exported and sent back via email</div>
        </div>
      </div>
    </div>

  </div>
</div>
""", unsafe_allow_html=True)

styles.footer()
