"""
ui_common.py · Shared UI styling, layout, and sidebar across all pages
Guarantees:
  1. Main content has dark crisp text (#0f172a) on light backgrounds.
  2. Sidebar has PURE BRIGHT WHITE (#ffffff) text on dark navy background.
  3. No duplicate emojis or invisible navigation links.
"""

import streamlit as st
import text


def apply_custom_css():
    st.markdown("""
    <style>
    /* =========================================================
       1. GLOBAL THEME & MAIN CONTENT STYLING
       ========================================================= */
    .stApp {
        background-color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Scoped strictly to MAIN content area: dark charcoal text */
    [data-testid="stMain"],
    [data-testid="stMain"] p,
    [data-testid="stMain"] div[data-testid="stMarkdownContainer"] p,
    [data-testid="stMain"] div[data-testid="stMarkdownContainer"] li,
    .main p {
        color: #0f172a !important;
    }
    
    /* Main Area Headings */
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] h5,
    [data-testid="stMain"] h6 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    /* Captions & Subtitles in Main */
    [data-testid="stMain"] .stCaption, 
    [data-testid="stMain"] [data-testid="stCaptionContainer"],
    [data-testid="stMain"] [data-testid="stCaptionContainer"] p {
        color: #475569 !important;
        font-size: 0.92rem !important;
    }
    
    /* Form & Input Labels in Main */
    [data-testid="stMain"] [data-testid="stWidgetLabel"] label,
    [data-testid="stMain"] [data-testid="stWidgetLabel"] p {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Text & Number Inputs in Main */
    [data-testid="stMain"] .stTextInput input, 
    [data-testid="stMain"] .stNumberInput input {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    
    /* =========================================================
       2. TABS: Side-by-side, full-width, clean
       ========================================================= */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        gap: 12px !important;
        border-bottom: 2px solid #e2e8f0 !important;
        margin-bottom: 20px !important;
    }
    button[data-baseweb="tab"] {
        flex: 1 1 0% !important;
        text-align: center !important;
        justify-content: center !important;
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 16px !important;
        border-radius: 8px 8px 0 0 !important;
        background-color: #f1f5f9 !important;
        border: 1px solid #e2e8f0 !important;
        border-bottom: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #059669 !important;
        background-color: #ffffff !important;
        border-top: 3px solid #059669 !important;
        border-bottom: 2px solid #ffffff !important;
        margin-bottom: -2px !important;
    }
    
    /* Bordered Containers (Cards) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* Primary buttons */
    .stButton>button[kind="primary"] {
        background-color: #059669 !important;
        border: 1px solid #059669 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #047857 !important;
    }
    
    /* =========================================================
       3. SIDEBAR: PURE BRIGHT WHITE (#ffffff) TEXT GUARANTEED
       ========================================================= */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    
    /* Force ALL sidebar text, links, spans, and labels to pure bright white */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] a,
    [data-testid="stSidebarNav"] *,
    [data-testid="stSidebarNavLink"] *,
    [data-testid="stSidebarNavLink"] span,
    [data-testid="stSidebarNavItems"] *,
    [data-testid="stSidebarNavItems"] span,
    ul[data-testid="stSidebarNavItems"] span,
    ul[data-testid="stSidebarNavItems"] a,
    ul[data-testid="stSidebarNavItems"] div,
    div[data-testid="stSidebarNav"] span {
        color: #ffffff !important;
        fill: #ffffff !important;
        opacity: 1 !important;
        visibility: visible !important;
        font-size: 0.96rem !important;
        font-weight: 600 !important;
    }
    
    /* Make navigation labels bold and clearly readable */
    [data-testid="stSidebarNavLink"] span {
        color: #ffffff !important;
        display: inline-block !important;
    }
    
    /* Active navigation item: crisp emerald highlight with white text */
    [data-testid="stSidebarNavLink"][aria-current="page"] {
        background-color: #059669 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebarNavLink"][aria-current="page"] span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Hover on nav links */
    [data-testid="stSidebarNavLink"]:hover {
        background-color: #1e293b !important;
        border-radius: 8px !important;
    }
    
    /* Section headers in sidebar navigation */
    [data-testid="stSidebarNav"] div[data-testid="stSidebarNavSeparator"] + div,
    [data-testid="stSidebarNav"] h2,
    [data-testid="stSidebarNav"] h3 {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-weight: 700 !important;
    }
    
    /* Radio buttons in sidebar */
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio div {
        color: #ffffff !important;
    }
    
    /* Buttons in sidebar */
    section[data-testid="stSidebar"] button {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _on_sidebar_lang_change():
    chosen = st.session_state.get("sidebar_lang_selector")
    st.session_state["lang"] = "kn" if chosen == "ಕನ್ನಡ" else "en"


def render_sidebar():
    """Consistent sidebar across pages"""
    current_lang = st.session_state.get("lang", "en")

    with st.sidebar:
        st.markdown(f"<h2 style='color:#ffffff; margin-bottom:2px;'>{text.T('app_title', current_lang)}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#94a3b8; font-size:0.85em; margin-bottom:14px;'>{text.T('app_subtitle', current_lang)}</div>", unsafe_allow_html=True)
        st.divider()

        user = st.session_state.get("user")
        if user:
            # Language switcher in sidebar for logged in users
            st.radio(
                text.T("sidebar_lang_label", current_lang),
                options=["English", "ಕನ್ನಡ"],
                index=0 if current_lang == "en" else 1,
                horizontal=True,
                key="sidebar_lang_selector",
                on_change=_on_sidebar_lang_change
            )
            st.divider()

            # User profile card
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155; padding:12px; border-radius:10px; margin-bottom:14px;">
                <div style="font-size:0.75em; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;">{text.T('sidebar_logged_in', current_lang)}</div>
                <div style="font-size:1.05em; font-weight:700; color:#ffffff;">👤 {user['name']}</div>
                <div style="font-size:0.85em; color:#cbd5e1;">📞 {user['phone']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Logout button
            if st.button(text.T("sidebar_logout", current_lang), use_container_width=True, type="secondary"):
                st.session_state["user"] = None
                st.rerun()
        else:
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155; padding:12px; border-radius:10px; color:#ffffff; font-size:0.9em; margin-bottom:14px;">
                {text.T('sidebar_please_login', current_lang)}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#cbd5e1; font-size:0.85em;'>{text.T('sidebar_helpline', current_lang)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#cbd5e1; font-size:0.85em;'>{text.T('sidebar_mithra', current_lang)}</div>", unsafe_allow_html=True)


def rupees(x):
    n = int(round(x))
    s = str(abs(n))
    if len(s) > 3:
        head, tail, parts = s[:-3], s[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        s = (",".join([head] + parts) if head else ",".join(parts)) + "," + tail
    return ("-" if n < 0 else "") + "₹" + s
