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
    user_info  = _get_user_info(token_data["access_token"])
    email      = user_info.get("email", "")
    admin_email = _cfg("ADMIN_EMAIL")
    if email and email == admin_email:
        st.session_state["is_admin"]    = True
        st.session_state["admin_email"] = email
    else:
        st.session_state["_oauth_error"] = f"{email} is not authorised."
    st.query_params.clear()
    st.rerun()


def is_admin() -> bool:
    return st.session_state.get("is_admin", False)


def admin_widget() -> None:
    _handle_callback()

    st.sidebar.markdown("""
    <style>
    /* Admin section divider label */
    .admin-label {
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 3px;
        color: #334155;
        text-transform: uppercase;
        margin: 0 0 10px 0;
    }
    /* Logged-in badge */
    .admin-badge {
        background: rgba(5,150,105,0.15);
        border: 1px solid rgba(5,150,105,0.35);
        border-radius: 8px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }
    .admin-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #059669;
        flex-shrink: 0;
        box-shadow: 0 0 6px #05966988;
    }
    .admin-badge-text {
        font-size: 11px;
        font-weight: 700;
        color: #6EE7B7;
        line-height: 1.3;
    }
    .admin-badge-sub {
        font-size: 10px;
        color: #475569;
        margin-top: 1px;
    }
    /* Password input on dark sidebar */
    [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
        color: #F1F5F9 !important;
        font-size: 13px !important;
        padding: 8px 12px !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: rgba(96,165,250,0.5) !important;
        box-shadow: 0 0 0 2px rgba(96,165,250,0.15) !important;
    }
    [data-testid="stSidebar"] .stTextInput label {
        font-size: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        color: #475569 !important;
    }
    /* Login button */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(37,99,235,0.9) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        padding: 8px 0 !important;
        width: 100% !important;
        transition: background 0.2s !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(37,99,235,1) !important;
    }
    /* Google link button */
    [data-testid="stSidebar"] .stLinkButton a {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
        color: #CBD5E1 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        padding: 8px 0 !important;
        transition: border-color 0.2s, color 0.2s !important;
    }
    [data-testid="stSidebar"] .stLinkButton a:hover {
        border-color: rgba(96,165,250,0.5) !important;
        color: #60A5FA !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.divider()
    st.sidebar.markdown('<div class="admin-label">Admin</div>', unsafe_allow_html=True)

    if is_admin():
        email = st.session_state.get("admin_email", "admin")
        st.sidebar.markdown(
            f'<div class="admin-badge">'
            f'<div class="admin-dot"></div>'
            f'<div>'
            f'<div class="admin-badge-text">Admin Mode</div>'
            f'<div class="admin-badge-sub">{email}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state["is_admin"]    = False
            st.session_state["admin_email"] = ""
            st.session_state["_oauth_done"] = False
            st.rerun()
    else:
        if st.session_state.get("_oauth_error"):
            st.sidebar.error(st.session_state.pop("_oauth_error"))

        if _cfg("GOOGLE_CLIENT_ID"):
            st.sidebar.link_button(
                "Continue with Google",
                _google_auth_url(),
                use_container_width=True,
            )
            st.sidebar.markdown(
                '<div style="text-align:center;color:#334155;font-size:10px;'
                'margin:6px 0;font-weight:600">or</div>',
                unsafe_allow_html=True,
            )

        pwd = st.sidebar.text_input("Password", type="password", key="admin_pwd_input",
                                    label_visibility="collapsed",
                                    placeholder="Admin password")
        if st.sidebar.button("Sign in", use_container_width=True, key="admin_login_btn"):
            if pwd == _cfg("ADMIN_PASSWORD", "bracuduburi2026"):
                st.session_state["is_admin"]    = True
                st.session_state["admin_email"] = "admin"
                st.rerun()
            else:
                st.sidebar.error("Incorrect password")
