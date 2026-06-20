import streamlit as st
from utils import styles, auth

st.set_page_config(
    page_title="BRACU Duburi — Vision Pipeline",
    page_icon="🤿",
    layout="wide",
    initial_sidebar_state="expanded",
)
styles.inject()

# Sidebar branding + admin — shared across all pages
with st.sidebar:
    st.markdown("## BRACU Duburi")
    st.markdown(
        "<p style='color:#60A5FA;font-size:11px;font-weight:600;letter-spacing:2px'>"
        "VISION PIPELINE</p>",
        unsafe_allow_html=True,
    )
    st.divider()
    auth.admin_widget()

pg = st.navigation([
    st.Page("pages/home.py",             title="Home",                icon="🏠"),
    st.Page("pages/1_About.py",          title="About Competition",   icon="🏆"),
    st.Page("pages/2_Tasks.py",          title="Competition Tasks",   icon="🎯"),
    st.Page("pages/3_Pipeline.py",       title="Automation Pipeline", icon="⚙️"),
    st.Page("pages/4_Task_Analytics.py", title="Task Analytics",      icon="📊"),
])
pg.run()
