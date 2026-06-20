import streamlit as st


def _password() -> str:
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        return "bracuduburi2026"


def is_admin() -> bool:
    return st.session_state.get("is_admin", False)


def admin_widget() -> None:
    st.sidebar.divider()
    if is_admin():
        st.sidebar.success("Admin mode")
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()
    else:
        with st.sidebar.expander("Admin Login"):
            pwd = st.text_input("Password", type="password", key="admin_pwd_input")
            if st.button("Login", key="admin_login_btn", use_container_width=True):
                if pwd == _password():
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
