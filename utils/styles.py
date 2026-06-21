import streamlit as st


SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #EEF2F7; }
.block-container { padding-top: 1rem !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1B2A 0%, #1B3A5C 100%);
    border-right: none;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stMarkdown { color: #CBD5E1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #F1F5F9 !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] [data-baseweb="select"] {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.15) !important;
    color: #F1F5F9 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12); }
[data-testid="stSidebar"] .stCaption { color: #64748B !important; }

.hero-banner {
    background: linear-gradient(135deg, #0D1B2A 0%, #1B3A5C 50%, #0E4D8C 100%);
    padding: 36px 40px;
    border-radius: 16px;
    margin: 8px 0 28px 0;
    text-align: center;
    box-shadow: 0 8px 32px rgba(13,27,42,0.25);
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 42px;
    color: #FFFFFF;
    letter-spacing: 5px;
    margin: 0 0 6px 0;
    text-shadow: 0 4px 24px rgba(0,0,0,0.4);
    line-height: 1.15;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #60A5FA;
    letter-spacing: 5px;
    text-transform: uppercase;
    margin: 0;
}
.hero-extra {
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.45);
    margin-top: 14px;
    letter-spacing: 1px;
}

.page-header {
    background: linear-gradient(135deg, #0D1B2A 0%, #1B3A5C 100%);
    padding: 28px 36px;
    border-radius: 14px;
    margin: 0 0 24px 0;
    box-shadow: 0 4px 20px rgba(13,27,42,0.2);
}
.page-header-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 32px;
    color: #FFFFFF;
    letter-spacing: 4px;
    margin: 0 0 4px 0;
    line-height: 1.1;
}
.page-header-sub {
    font-size: 11px;
    font-weight: 600;
    color: #60A5FA;
    letter-spacing: 4px;
    text-transform: uppercase;
}

.section-header {
    font-size: 12px;
    font-weight: 800;
    color: #1E3A5F;
    text-transform: uppercase;
    letter-spacing: 3px;
    border-left: 4px solid #2563EB;
    padding: 6px 0 6px 14px;
    margin: 0 0 18px 0;
    background: rgba(37,99,235,0.04);
    border-radius: 0 6px 6px 0;
}

.card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 24px 20px;
    box-shadow: 0 2px 16px rgba(13,27,42,0.07);
    height: 100%;
}

.metric-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 22px 20px 18px 20px;
    text-align: center;
    box-shadow: 0 2px 16px rgba(13,27,42,0.08);
    border-top: 5px solid #2563EB;
    height: 100%;
}
.metric-card.green  { border-top-color: #059669; }
.metric-card.purple { border-top-color: #7C3AED; }
.metric-card.cyan   { border-top-color: #0891B2; }
.metric-card.amber  { border-top-color: #D97706; }
.metric-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #94A3B8;
    margin-bottom: 10px;
}
.metric-value {
    font-size: 34px;
    font-weight: 900;
    color: #0F172A;
    line-height: 1;
}
.metric-sub { font-size: 11px; color: #94A3B8; margin-top: 6px; }

.step-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 18px 14px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(13,27,42,0.07);
    height: 100%;
}
.step-num {
    width: 28px; height: 28px;
    background: #2563EB;
    color: #fff;
    border-radius: 50%;
    font-size: 12px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 10px auto;
}
.step-title {
    font-size: 12px;
    font-weight: 800;
    color: #0F172A;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.task-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 24px 20px;
    box-shadow: 0 2px 16px rgba(13,27,42,0.07);
    border-left: 5px solid var(--task-color, #2563EB);
    height: 100%;
    transition: box-shadow 0.2s;
}
.task-card:hover { box-shadow: 0 4px 24px rgba(13,27,42,0.13); }

hr { border-color: #E2E8F0 !important; margin: 24px 0 !important; }

footer { visibility: hidden; }
</style>
"""


def inject() -> None:
    st.markdown(SHARED_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<div class="page-header-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-header-title">{title}</div>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, sub: str = "", color: str = "") -> None:
    cls = f"metric-card {color}".strip()
    st.markdown(
        f'<div class="{cls}">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        "<p style='text-align:center;color:#CBD5E1;font-size:11px;font-weight:600;"
        "letter-spacing:2px;margin-top:40px'>"
        "BRACU DUBURI &nbsp;|&nbsp; VISION PIPELINE AUTOMATION &nbsp;|&nbsp; AUV OBJECT DETECTION"
        "</p>",
        unsafe_allow_html=True,
    )
