import streamlit as st
from utils import styles, content, auth

st.set_page_config(
    page_title="Competition Tasks — BRACU Duburi",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)
styles.inject()

data = content.load()
tasks = data.get("tasks", [])

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

styles.page_header("Competition Tasks", "RoboSub 2026 · Underwater Challenges")

if auth.is_admin():
    st.info("**Admin mode** — expand any task card to edit its name and description.", icon="🔒")

changed = False
for i, task in enumerate(tasks):
    color = task.get("color", "#2563EB")

    with st.expander(f"**{task.get('name', f'Task {i+1}')}**", expanded=False):
        col1, col2 = st.columns([3, 1])

        with col1:
            if auth.is_admin():
                new_name = st.text_input("Task Name", value=task.get("name", ""), key=f"tname_{i}")
                new_desc = st.text_area(
                    "Description",
                    value=task.get("description", ""),
                    height=100,
                    key=f"tdesc_{i}",
                )
                new_run  = st.text_input(
                    "Saved Run Folder Name",
                    value=task.get("run_name", ""),
                    key=f"trun_{i}",
                    help="Folder name inside saved_runs/ to link analytics to this task",
                )
                new_color = st.color_picker("Accent Color", value=color, key=f"tcolor_{i}")

                if st.button("Update Task", key=f"tsave_{i}", type="primary"):
                    tasks[i]["name"]        = new_name
                    tasks[i]["description"] = new_desc
                    tasks[i]["run_name"]    = new_run
                    tasks[i]["color"]       = new_color
                    data["tasks"] = tasks
                    content.save(data)
                    st.success("Task updated!")
                    st.rerun()
            else:
                st.markdown(f"**{task.get('name', '')}**")
                st.markdown(task.get("description", ""))

        with col2:
            st.markdown(
                f'<div style="background:{color};border-radius:50%;width:64px;height:64px;'
                f'display:flex;align-items:center;justify-content:center;margin:auto;'
                f'box-shadow:0 4px 16px {color}66">'
                f'<span style="font-size:28px">🎯</span>'
                f'</div>'
                f'<p style="text-align:center;font-size:11px;color:{color};font-weight:800;'
                f'margin-top:10px;text-transform:uppercase;letter-spacing:1px">'
                f'{task.get("name","")}</p>',
                unsafe_allow_html=True,
            )

styles.footer()
