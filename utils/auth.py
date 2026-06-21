from urllib.parse import urlencode
import streamlit as st
import requests as _req


def _cfg(key: str, fallback: str = "") -> str:
    try:
        return st.secrets[key]
    except Exception:
        return fallback


def _google_auth_url() -> str:
    params = {
        "client_id":     _cfg("GOOGLE_CLIENT_ID"),
        "redirect_uri":  _cfg("REDIRECT_URI"),
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"


def _exchange_code(code: str) -> dict:
    try:
        resp = _req.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code":          code,
                "client_id":     _cfg("GOOGLE_CLIENT_ID"),
                "client_secret": _cfg("GOOGLE_CLIENT_SECRET"),
                "redirect_uri":  _cfg("REDIRECT_URI"),
                "grant_type":    "authorization_code",
            },
            timeout=10,
        )
        return resp.json()
    except Exception:
        return {}


def _get_user_info(access_token: str) -> dict:
    try:
        resp = _req.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        return resp.json()
    except Exception:
        return {}


def _handle_callback() -> None:
    code = st.query_params.get("code")
    if not code or st.session_state.get("_oauth_done"):
        return
    st.session_state["_oauth_done"] = True
    token_data = _exchange_code(code)
    if "access_token" not in token_data:
        st.session_state["_oauth_error"] = "Token exchange failed."
        st.query_params.clear()
        return
    user_info = _get_user_info(token_data["access_token"])
    email = user_info.get("email", "")
    admin_email = _cfg("ADMIN_EMAIL")
    if email and email == admin_email:
        st.session_state["is_admin"]    = True
        st.session_state["admin_email"] = email
    else:
        st.session_state["_oauth_error"] = f"{email} is not authorised as admin."
    st.query_params.clear()
    st.rerun()


def is_admin() -> bool:
    return st.session_state.get("is_admin", False)


def admin_widget() -> None:
    _handle_callback()

    st.sidebar.divider()
    if is_admin():
        email = st.session_state.get("admin_email", "")
        st.sidebar.success(f"Admin: {email}")
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state["is_admin"]    = False
            st.session_state["admin_email"] = ""
            st.session_state["_oauth_done"] = False
            st.rerun()
    else:
        if st.session_state.get("_oauth_error"):
            st.sidebar.error(st.session_state.pop("_oauth_error"))
        client_id = _cfg("GOOGLE_CLIENT_ID")
        if client_id:
            st.sidebar.link_button(
                "Login with Google",
                _google_auth_url(),
                use_container_width=True,
            )
        with st.sidebar.expander("Admin Login"):
            pwd = st.text_input("Password", type="password", key="admin_pwd_input")
            if st.button("Login", key="admin_login_btn", use_container_width=True):
                if pwd == _cfg("ADMIN_PASSWORD", "bracuduburi2026"):
                    st.session_state["is_admin"]    = True
                    st.session_state["admin_email"] = "admin"
                    st.rerun()
                else:
                    st.error("Incorrect password")
