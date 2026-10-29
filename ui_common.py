"""
ui_common.py · Shared UI styling, layout, and sidebar across all pages
Guarantees high contrast, professional typography, and full visibility in all themes.
"""

import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
    /* =========================================================
       1. GLOBAL THEME & VISIBILITY OVERRIDES (STRICT CONTRAST)
       ========================================================= */
    .stApp {
        background-color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Ensure all text, paragraphs, and markdown are dark and crisp */
    .stApp, 
    .stApp p, 
    .stApp span, 
    .stApp div[data-testid="stMarkdownContainer"] p,
    .stApp div[data-testid="stMarkdownContainer"] li {
        color: #0f172a !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    /* Captions & Subtitles */
    .stCaption, 
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: #475569 !important;
        font-size: 0.92rem !important;
    }
    
    /* Form & Input Labels */
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Text & Number Inputs */
    .stTextInput input, 
    .stNumberInput input {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    .stTextInput input:focus, 
    .stNumberInput input:focus {
        border-color: #059669 !important;
        box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2) !important;
    }
    
    /* Tabs Visibility */
    button[data-baseweb="tab"] {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #059669 !important;
        border-bottom-color: #059669 !important;
    }
    
    /* Bordered Containers (Cards) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* Buttons */
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
        border-color: #047857 !important;
    }
    .stButton>button[kind="secondary"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        color: #1e293b !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #f1f5f9 !important;
        border-color: #94a3b8 !important;
    }
    
    /* Metrics display */
    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    
    /* =========================================================
       2. DARK SIDEBAR STYLING
       ========================================================= */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] button {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #334155 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Consistent sidebar across every page: user status, language, logout, helpline"""
    with st.sidebar:
        st.markdown("<h2 style='color:#f8fafc; margin-bottom:2px;'>⚡ Power Bill Coach</h2>", unsafe_allow_html=True)
        st.markdown("<div style='color:#94a3b8; font-size:0.85em; margin-bottom:14px;'>Karnataka · BESCOM Domestic Advisor</div>", unsafe_allow_html=True)
        st.divider()

        user = st.session_state.get("user")
        if user:
            # User profile card
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155; padding:12px; border-radius:10px; margin-bottom:14px;">
                <div style="font-size:0.75em; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;">Logged In As</div>
                <div style="font-size:1.05em; font-weight:700; color:#f8fafc;">👤 {user['name']}</div>
                <div style="font-size:0.85em; color:#cbd5e1;">📞 {user['phone']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Language switcher
            current_lang = st.session_state.get("lang", "en")
            lang_choice = st.radio(
                "Language / ಭಾಷೆ",
                options=["English", "ಕನ್ನಡ"],
                index=0 if current_lang == "en" else 1,
                horizontal=True,
                key="sidebar_lang_selector"
            )
            st.session_state["lang"] = "en" if lang_choice == "English" else "kn"

            st.divider()

            # Logout button
            if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
                st.session_state["user"] = None
                st.rerun()
        else:
            # Not logged in
            st.markdown("""
            <div style="background:#1e293b; border:1px solid #334155; padding:12px; border-radius:10px; color:#cbd5e1; font-size:0.9em; margin-bottom:14px;">
                🔐 Please log in to view your household bills and insights.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='color:#94a3b8; font-size:0.85em;'>☎️ <b>BESCOM Helpline:</b> 1912</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#94a3b8; font-size:0.85em;'>📱 <b>BESCOM Mithra App</b> for official meter complaints</div>", unsafe_allow_html=True)


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
