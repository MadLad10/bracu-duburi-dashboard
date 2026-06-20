import streamlit as st
from utils import styles, content, auth

st.set_page_config(
    page_title="About — BRACU Duburi",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)
styles.inject()

data = content.load()
about = data.get("about", {})

with st.sidebar:
    st.markdown("## BRACU Duburi")
    st.markdown(
        "<p style='color:#60A5FA;font-size:11px;font-weight:600;letter-spacing:2px'>"
        "VISION PIPELINE</p>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.page_link("dashboard.py",              label="Home",               icon="🏠")
    st.page_link("pages/1_About.py",          label="About Competition",  icon="🏆")
    st.page_link("pages/2_Tasks.py",          label="Competition Tasks",  icon="🎯")
    st.page_link("pages/3_Pipeline.py",       label="Automation Pipeline", icon="⚙️")
    st.page_link("pages/4_Task_Analytics.py", label="Task Analytics",     icon="📊")
    auth.admin_widget()

styles.page_header("About the Competition", "RoboSub 2026 · International AUV Challenge")

# ── Content ───────────────────────────────────────────────────────────────────
if auth.is_admin():
    st.info("**Admin mode** — you can edit the content below and save changes.", icon="🔒")

col1, col2 = st.columns([3, 2])

with col1:
    styles.section("About RoboSub")
    if auth.is_admin():
        new_comp_name = st.text_input("Competition Name", value=about.get("competition_name", ""))
        new_comp_desc = st.text_area(
            "Competition Description",
            value=about.get("competition_description", ""),
            height=150,
        )
        new_venue = st.text_input("Venue", value=about.get("venue", ""))
        new_date  = st.text_input("Date",  value=about.get("date",  ""))
    else:
        st.markdown(f"### {about.get('competition_name', 'RoboSub 2026')}")
        st.markdown(about.get("competition_description", ""))
        st.markdown(
            f"📍 **Venue:** {about.get('venue', '')}  \n"
            f"📅 **Date:** {about.get('date', '')}",
        )

with col2:
    styles.section("About Our Team")
    if auth.is_admin():
        new_team_desc = st.text_area(
            "Team Description",
            value=about.get("team_description", ""),
            height=200,
        )
    else:
        st.markdown(about.get("team_description", ""))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="background:#0D1B2A;border-radius:12px;padding:18px 20px;color:#CBD5E1">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:22px;color:#60A5FA;letter-spacing:3px">BRACU DUBURI</div>'
        '<div style="font-size:12px;margin-top:4px">BRAC University · Dhaka, Bangladesh</div>'
        '<div style="font-size:11px;color:#475569;margin-top:8px">Competing since 2019</div>'
        '</div>',
        unsafe_allow_html=True,
    )

if auth.is_admin():
    st.divider()
    if st.button("Save Changes", type="primary", use_container_width=False):
        data["about"]["competition_name"]        = new_comp_name
        data["about"]["competition_description"] = new_comp_desc
        data["about"]["venue"]                   = new_venue
        data["about"]["date"]                    = new_date
        data["about"]["team_description"]        = new_team_desc
        content.save(data)
        st.success("Changes saved!")
        st.rerun()

styles.footer()
