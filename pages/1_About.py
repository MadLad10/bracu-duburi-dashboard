import streamlit as st
from utils import styles, content, auth

data = content.load()
about = data.get("about", {})

styles.page_header("About the Competition", "RoboSub 2026 · Woollett Aquatics Center, Irvine, CA")

if auth.is_admin():
    st.info("**Admin mode** — edit the content below and save.")

# ── Key facts banner ──────────────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns(4)
with f1: styles.metric_card("Event",    "RoboSub 2026", "International AUV Competition", "")
with f2: styles.metric_card("Dates",    "Jul 11–16",    "2026",                           "green")
with f3: styles.metric_card("Location", "Irvine, CA",   "Woollett Aquatics Center",       "purple")
with f4: styles.metric_card("Format",   "Autonomous",   "Zero human control during run",  "amber")

st.markdown("<br>", unsafe_allow_html=True)

# ── About RoboSub + Team side by side ────────────────────────────────────────
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    styles.section("What is RoboSub?")
    if auth.is_admin():
        new_comp_name = st.text_input("Competition Name", value=about.get("competition_name", ""))
        new_comp_desc = st.text_area("Competition Description",
                                     value=about.get("competition_description", ""), height=140)
    else:
        st.markdown(
            f'<div style="background:#FFFFFF;border-radius:12px;padding:22px 24px;'
            f'box-shadow:0 2px 16px rgba(13,27,42,0.06);border-left:4px solid #2563EB">'
            f'<p style="color:#334155;font-size:14px;line-height:1.8;margin:0">'
            f'{about.get("competition_description", "")}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    styles.section("Competition Format")
    if auth.is_admin():
        new_format = st.text_area("Format Description",
                                  value=about.get("format", ""), height=110)
    else:
        stages = [
            ("01", "Design & Build",     "Teams assemble and develop all AUV sub-systems from scratch."),
            ("02", "Underwater Tasks",   "Vehicles complete a series of tasks fully autonomously — gates, buoys, bins, torpedoes, and surfacing."),
            ("03", "Scoring & Awards",   "Points determine rankings. Prize money and recognition are awarded to top teams."),
        ]
        for num, title, desc in stages:
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:14px;'
                f'background:#FFFFFF;border-radius:10px;padding:14px 16px;'
                f'box-shadow:0 1px 8px rgba(13,27,42,0.06);margin-bottom:10px">'
                f'<div style="min-width:28px;height:28px;background:#2563EB;border-radius:50%;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:11px;font-weight:800;color:#fff">{num}</div>'
                f'<div><div style="font-size:13px;font-weight:800;color:#0F172A;margin-bottom:3px">'
                f'{title}</div>'
                f'<div style="font-size:12px;color:#64748B;line-height:1.5">{desc}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

with col2:
    styles.section("About Our Team")
    if auth.is_admin():
        new_team_desc = st.text_area("Team Description",
                                     value=about.get("team_description", ""), height=160)
    else:
        st.markdown(
            f'<div style="background:#FFFFFF;border-radius:12px;padding:22px 24px;'
            f'box-shadow:0 2px 16px rgba(13,27,42,0.06);border-left:4px solid #059669">'
            f'<p style="color:#334155;font-size:13px;line-height:1.8;margin:0">'
            f'{about.get("team_description", "")}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Team identity card
    st.markdown(
        '<div style="background:linear-gradient(135deg,#0D1B2A,#1B3A5C);border-radius:12px;'
        'padding:22px 20px;color:#CBD5E1">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:26px;color:#60A5FA;'
        'letter-spacing:3px;margin-bottom:4px">BRACU DUBURI</div>'
        '<div style="font-size:12px;color:#94A3B8;margin-bottom:16px">'
        'BRAC University · Dhaka, Bangladesh</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'
        '<div style="background:rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px">'
        '<div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1px">University</div>'
        '<div style="font-size:13px;font-weight:700;color:#F1F5F9;margin-top:2px">BRAC University</div>'
        '</div>'
        '<div style="background:rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px">'
        '<div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1px">Country</div>'
        '<div style="font-size:13px;font-weight:700;color:#F1F5F9;margin-top:2px">Bangladesh</div>'
        '</div>'
        '<div style="background:rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px">'
        '<div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1px">Detection</div>'
        '<div style="font-size:13px;font-weight:700;color:#F1F5F9;margin-top:2px">YOLO</div>'
        '</div>'
        '<div style="background:rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px">'
        '<div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1px">Competition</div>'
        '<div style="font-size:13px;font-weight:700;color:#F1F5F9;margin-top:2px">RoboSub 2026</div>'
        '</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Venue info
    styles.section("Venue")
    if auth.is_admin():
        new_venue = st.text_input("Venue", value=about.get("venue", ""))
        new_date  = st.text_input("Date",  value=about.get("date",  ""))
    else:
        st.markdown(
            f'<div style="background:#FFFFFF;border-radius:10px;padding:14px 16px;'
            f'box-shadow:0 1px 8px rgba(13,27,42,0.06)">'
            f'<div style="font-size:13px;font-weight:700;color:#0F172A">'
            f'{about.get("venue","")}</div>'
            f'<div style="font-size:12px;color:#64748B;margin-top:4px">'
            f'{about.get("date","")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Admin save ────────────────────────────────────────────────────────────────
if auth.is_admin():
    st.divider()
    if st.button("Save Changes", type="primary"):
        data["about"]["competition_name"]        = new_comp_name
        data["about"]["competition_description"] = new_comp_desc
        data["about"]["format"]                  = new_format
        data["about"]["venue"]                   = new_venue
        data["about"]["date"]                    = new_date
        data["about"]["team_description"]        = new_team_desc
        content.save(data)
        st.success("Changes saved!")
        st.rerun()

styles.footer()
