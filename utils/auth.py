import streamlit as st


def _credentials() -> tuple[str, str]:
    try:
        return st.secrets["ADMIN_USERNAME"], st.secrets["ADMIN_PASSWORD"]
    except Exception:
        return "myuser", "abcdef"


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
            usr = st.text_input("Username", key="admin_usr_input")
            pwd = st.text_input("Password", type="password", key="admin_pwd_input")
            if st.button("Login", key="admin_login_btn", use_container_width=True):
                valid_usr, valid_pwd = _credentials()
                if usr == valid_usr and pwd == valid_pwd:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Incorrect credentials")
