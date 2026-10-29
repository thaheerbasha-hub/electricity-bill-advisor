"""
ui_common.py · Global Theme Engine & Multi-Theme Styling
Supports 5 distinct visual design themes:
  1. Classic Clean (Default) · Original light/navy layout
  2. Neon Glass · Dark glassmorphism with blur and glowing borders
  3. Soft Clay · Soft 3D pastel elements with rounded shadows
  4. Cozy Wool · Textured fabric look with stitched borders
  5. Smooth Tactile · Monochromatic neumorphic soft-UI
"""

import textwrap
import streamlit as st
import text

THEMES = {
    "classic": "Classic Clean (Default)",
    "neon_glass": "Neon Glass",
    "soft_clay": "Soft Clay",
    "cozy_wool": "Cozy Wool",
    "smooth_tactile": "Smooth Tactile"
}

THEME_DISPLAY_TO_KEY = {v: k for k, v in THEMES.items()}


def get_current_theme():
    """Retrieve active theme from query params, session state, or default to classic."""
    qp_theme = st.query_params.get("theme")
    if qp_theme and qp_theme in THEMES:
        st.session_state["theme"] = qp_theme
        return qp_theme

    if "theme" in st.session_state and st.session_state["theme"] in THEMES:
        return st.session_state["theme"]

    st.session_state["theme"] = "classic"
    return "classic"


def _on_theme_dropdown_change():
    """Callback when user changes theme in sidebar."""
    chosen_label = st.session_state.get("global_sidebar_theme_selector")
    chosen_key = THEME_DISPLAY_TO_KEY.get(chosen_label, "classic")
    st.session_state["theme"] = chosen_key
    st.query_params["theme"] = chosen_key


def apply_custom_css():
    """Inject the active theme CSS and localStorage persistence script using st.html."""
    active_theme = get_current_theme()

    # Browser JavaScript to keep localStorage in sync and restore on cold visit
    storage_sync_js = f"""
    <script>
    (function() {{
        try {{
            const active = "{active_theme}";
            localStorage.setItem("pbc_active_theme", active);

            // Cold start check: if URL has no ?theme=, redirect to saved preference
            const url = new URL(window.location.href);
            const qp = url.searchParams.get("theme");
            const stored = localStorage.getItem("pbc_active_theme");
            if (stored && !qp && ["classic", "neon_glass", "soft_clay", "cozy_wool", "smooth_tactile"].includes(stored)) {{
                url.searchParams.set("theme", stored);
                window.location.replace(url.href);
            }}
        }} catch(e) {{}}
    }})();
    </script>
    """
    st.html(textwrap.dedent(storage_sync_js).strip(), unsafe_allow_javascript=True)

    # Base common structure: full-width tabs, neat layouts
    base_css = """
    /* Full width tabs styling across all themes */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        gap: 10px !important;
        margin-bottom: 20px !important;
    }
    button[data-baseweb="tab"] {
        flex: 1 1 0% !important;
        text-align: center !important;
        justify-content: center !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 10px 14px !important;
    }
    /* Ensure sidebar collapse arrow is visible */
    [data-testid="stSidebarCollapseButton"] button {
        opacity: 0.8 !important;
    }
    """

    # 1. CLASSIC CLEAN (DEFAULT)
    if active_theme == "classic":
        theme_css = """
        .stApp {
            background-color: #f8fafc !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        }
        [data-testid="stMain"], [data-testid="stMain"] p, [data-testid="stMain"] div[data-testid="stMarkdownContainer"] p, .main p {
            color: #0f172a !important;
        }
        [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4 {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.06) !important;
        }
        [data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 16px 20px !important;
            box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.06) !important;
        }
        [data-testid="stMetricLabel"] p {
            color: #64748b !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
        }
        [data-testid="stMetricValue"] div {
            color: #0f172a !important;
            font-size: 1.85rem !important;
            font-weight: 800 !important;
        }
        .stButton>button[kind="primary"] {
            background-color: #059669 !important;
            border: 1px solid #059669 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
        }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] *, [data-testid="stSidebarNavLink"] span {
            color: #ffffff !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: #059669 !important;
            border-radius: 8px !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        """

    # 2. NEON GLASS (Dark glassmorphism with blur and glowing borders)
    elif active_theme == "neon_glass":
        theme_css = """
        .stApp {
            background: radial-gradient(ellipse at 50% 15%, #1e133e 0%, #0d1224 45%, #04060f 100%) !important;
            background-attachment: fixed !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }
        [data-testid="stMain"], [data-testid="stMain"] p, [data-testid="stMain"] span, [data-testid="stMain"] div[data-testid="stMarkdownContainer"] p, .main p {
            color: #f1f5f9 !important;
        }
        [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4 {
            color: #ffffff !important;
            text-shadow: 0 0 16px rgba(168, 85, 247, 0.45) !important;
            font-weight: 800 !important;
        }
        [data-testid="stMain"] .stCaption, [data-testid="stMain"] [data-testid="stCaptionContainer"] p {
            color: #94a3b8 !important;
        }
        [data-testid="stMain"] [data-testid="stWidgetLabel"] label, [data-testid="stMain"] [data-testid="stWidgetLabel"] p {
            color: #e2e8f0 !important;
            font-weight: 600 !important;
        }
        /* Translucent Frosted Glass Cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(15, 23, 42, 0.62) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(168, 85, 247, 0.35) !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6), inset 0 0 16px rgba(168, 85, 247, 0.12) !important;
        }
        /* 4 Distinct Glowing Neon Metric Cards */
        [data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.6) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-radius: 18px !important;
            padding: 18px 20px !important;
            border: 1px solid rgba(168, 85, 247, 0.4) !important;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.5), inset 0 0 14px rgba(168, 85, 247, 0.12) !important;
        }
        [data-testid="column"]:nth-of-type(1) [data-testid="stMetric"] {
            border-color: rgba(56, 189, 248, 0.55) !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.25), inset 0 0 14px rgba(56, 189, 248, 0.12) !important;
        }
        [data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {
            border-color: rgba(96, 165, 250, 0.55) !important;
            box-shadow: 0 0 20px rgba(96, 165, 250, 0.25), inset 0 0 14px rgba(96, 165, 250, 0.12) !important;
        }
        [data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {
            border-color: rgba(168, 85, 247, 0.55) !important;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.25), inset 0 0 14px rgba(168, 85, 247, 0.12) !important;
        }
        [data-testid="column"]:nth-of-type(4) [data-testid="stMetric"] {
            border-color: rgba(244, 63, 94, 0.55) !important;
            box-shadow: 0 0 20px rgba(244, 63, 94, 0.25), inset 0 0 14px rgba(244, 63, 94, 0.12) !important;
        }
        [data-testid="stMetricLabel"] p {
            color: #cbd5e1 !important;
            font-weight: 600 !important;
        }
        [data-testid="stMetricValue"] div {
            color: #ffffff !important;
            font-weight: 800 !important;
            text-shadow: 0 0 12px rgba(255, 255, 255, 0.4) !important;
        }
        /* Inputs */
        [data-testid="stMain"] .stTextInput input, [data-testid="stMain"] .stNumberInput input {
            color: #ffffff !important;
            background-color: rgba(30, 41, 59, 0.75) !important;
            border: 1.5px solid rgba(139, 92, 246, 0.45) !important;
            border-radius: 10px !important;
            box-shadow: 0 0 12px rgba(139, 92, 246, 0.25) !important;
        }
        /* Buttons */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #7c3aed 0%, #2563eb 100%) !important;
            border: 1px solid #a855f7 !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            box-shadow: 0 0 18px rgba(124, 58, 237, 0.6) !important;
        }
        /* Sidebar in Neon Glass */
        section[data-testid="stSidebar"] {
            background: rgba(9, 14, 28, 0.96) !important;
            border-right: 1px solid rgba(168, 85, 247, 0.3) !important;
        }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] *, [data-testid="stSidebarNavLink"] span {
            color: #ffffff !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
            border-radius: 8px !important;
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.6) !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        """

    # 3. SOFT CLAY (Soft 3D pastel elements with rounded shadows)
    elif active_theme == "soft_clay":
        theme_css = """
        .stApp {
            background-color: #dff0fc !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }
        [data-testid="stMain"], [data-testid="stMain"] p, .main p {
            color: #1e293b !important;
        }
        [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4 {
            color: #0f172a !important;
            font-weight: 800 !important;
        }
        /* Claymorphic 3D Puffed Cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff !important;
            border: none !important;
            border-radius: 24px !important;
            box-shadow: 10px 14px 26px rgba(147, 178, 207, 0.45), inset -3px -3px 6px rgba(0, 0, 0, 0.04), inset 3px 3px 6px #ffffff !important;
        }
        /* 4 Pastel Candy Clay Metric Cards matching reference */
        [data-testid="stMetric"] {
            border-radius: 22px !important;
            padding: 18px 20px !important;
            border: none !important;
            box-shadow: 8px 10px 20px rgba(147, 178, 207, 0.4), inset -3px -3px 6px rgba(0, 0, 0, 0.05), inset 3px 3px 6px #ffffff !important;
        }
        [data-testid="column"]:nth-of-type(1) [data-testid="stMetric"] {
            background: #d7edfd !important; /* Pastel baby blue */
        }
        [data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {
            background: #d6f5f3 !important; /* Pastel mint cyan */
        }
        [data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {
            background: #ffdfe5 !important; /* Pastel soft peach/pink */
        }
        [data-testid="column"]:nth-of-type(4) [data-testid="stMetric"] {
            background: #fff1d4 !important; /* Pastel butter yellow */
        }
        [data-testid="stMetricLabel"] p {
            color: #475569 !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricValue"] div {
            color: #0f172a !important;
            font-weight: 800 !important;
            font-size: 1.85rem !important;
        }
        /* Puffy Clay Buttons */
        .stButton>button[kind="primary"] {
            background: #3b82f6 !important;
            border: none !important;
            color: #ffffff !important;
            border-radius: 18px !important;
            font-weight: 700 !important;
            box-shadow: inset -3px -3px 6px rgba(0, 0, 0, 0.2), inset 3px 3px 6px rgba(255, 255, 255, 0.4), 6px 8px 18px rgba(59, 130, 246, 0.35) !important;
        }
        /* Inputs with soft inset */
        [data-testid="stMain"] .stTextInput input, [data-testid="stMain"] .stNumberInput input {
            color: #0f172a !important;
            background-color: #f0f9ff !important;
            border: none !important;
            border-radius: 14px !important;
            box-shadow: inset 3px 3px 6px rgba(0, 0, 0, 0.08), inset -3px -3px 6px #ffffff !important;
        }
        /* Sidebar Soft Clay Style */
        section[data-testid="stSidebar"] {
            background-color: #d2e7f7 !important;
            border-right: 2px solid #b7d6ee !important;
        }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] * {
            color: #1e293b !important;
        }
        [data-testid="stSidebarNavLink"] span {
            color: #1e293b !important;
            font-weight: 700 !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: #bad9f5 !important;
            border-radius: 12px !important;
            box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.12), inset -2px -2px 5px #ffffff !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: #1d4ed8 !important;
        }
        """

    # 4. COZY WOOL (Textured fabric look with stitched borders)
    elif active_theme == "cozy_wool":
        theme_css = """
        .stApp {
            background-color: #f5efe4 !important;
            background-image: radial-gradient(#d6cbba 1.5px, transparent 1.5px) !important;
            background-size: 16px 16px !important;
            font-family: Georgia, Cambria, "Times New Roman", serif !important;
        }
        [data-testid="stMain"], [data-testid="stMain"] p, .main p {
            color: #2d241e !important;
        }
        [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4 {
            color: #1c1510 !important;
            font-weight: 700 !important;
        }
        /* Fabric Patch Stitched Cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #faf6ee !important;
            border: 2px dashed #a89880 !important;
            border-radius: 16px !important;
            box-shadow: 4px 4px 0px #cfc4b2 !important;
        }
        /* 4 Warm Wool Fabric Swatch Cards matching reference */
        [data-testid="stMetric"] {
            border-radius: 16px !important;
            padding: 16px 18px !important;
            border: 2px dashed #9c8e76 !important;
            box-shadow: 3px 3px 0px #cfc4b2 !important;
            font-family: Georgia, Cambria, serif !important;
        }
        [data-testid="column"]:nth-of-type(1) [data-testid="stMetric"] {
            background: #e5decb !important; /* Oatmeal tweed */
        }
        [data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {
            background: #eae2d3 !important; /* Khaki patch */
        }
        [data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {
            background: #f1ebd8 !important; /* Flaxen linen */
        }
        [data-testid="column"]:nth-of-type(4) [data-testid="stMetric"] {
            background: #d8c7af !important; /* Tan suede */
        }
        [data-testid="stMetricLabel"] p {
            color: #3e3328 !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricValue"] div {
            color: #1f1812 !important;
            font-weight: 800 !important;
        }
        /* Inputs styled like woven tags */
        [data-testid="stMain"] .stTextInput input, [data-testid="stMain"] .stNumberInput input {
            color: #2d241e !important;
            background-color: #f4eee4 !important;
            border: 1.5px dashed #a89f91 !important;
            border-radius: 10px !important;
        }
        /* Buttons like stitched fabric badge */
        .stButton>button[kind="primary"] {
            background-color: #236c39 !important;
            border: 2px dashed #ffffff !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 3px 3px 0px #144021 !important;
        }
        /* Sidebar: Dark Denim Felt with white stitching */
        section[data-testid="stSidebar"] {
            background-color: #1b2430 !important;
            border-right: 3px dashed #6b7c93 !important;
        }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] *, [data-testid="stSidebarNavLink"] span {
            color: #fbf8f2 !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: #236c39 !important;
            border: 2px dashed #ffffff !important;
            border-radius: 10px !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        """

    # 5. SMOOTH TACTILE (Monochromatic neumorphic soft-UI)
    elif active_theme == "smooth_tactile":
        theme_css = """
        .stApp {
            background-color: #e4e8ee !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }
        [data-testid="stMain"], [data-testid="stMain"] p, .main p {
            color: #2d3748 !important;
        }
        [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4 {
            color: #1a202c !important;
            font-weight: 700 !important;
        }
        /* Extruded Neumorphic Cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #e4e8ee !important;
            border: none !important;
            border-radius: 22px !important;
            box-shadow: 8px 8px 18px #c2c9d4, -8px -8px 18px #ffffff !important;
        }
        /* Extruded Neumorphic Metric Cards matching reference */
        [data-testid="stMetric"] {
            background: #e4e8ee !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 18px 20px !important;
            box-shadow: 8px 8px 18px #c2c9d4, -8px -8px 18px #ffffff !important;
        }
        [data-testid="stMetricLabel"] p {
            color: #64748b !important;
            font-weight: 600 !important;
        }
        [data-testid="stMetricValue"] div {
            color: #1a202c !important;
            font-weight: 800 !important;
        }
        /* Inset Neumorphic Inputs */
        [data-testid="stMain"] .stTextInput input, [data-testid="stMain"] .stNumberInput input {
            color: #2d3748 !important;
            background-color: #e4e8ee !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: inset 4px 4px 8px #c2c9d4, inset -4px -4px 8px #ffffff !important;
        }
        /* Extruded Buttons */
        .stButton>button[kind="primary"] {
            background: #e4e8ee !important;
            color: #059669 !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 14px !important;
            box-shadow: 6px 6px 14px #c2c9d4, -6px -6px 14px #ffffff !important;
        }
        .stButton>button[kind="primary"]:hover {
            box-shadow: inset 3px 3px 6px #c2c9d4, inset -3px -3px 6px #ffffff !important;
        }
        /* Neumorphic Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #e4e8ee !important;
            border-right: 1px solid #d5dce5 !important;
        }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] * {
            color: #2d3748 !important;
        }
        [data-testid="stSidebarNavLink"] span {
            color: #2d3748 !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] {
            background: #e4e8ee !important;
            border-radius: 12px !important;
            box-shadow: inset 4px 4px 8px #c2c9d4, inset -4px -4px 8px #ffffff !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: #059669 !important;
            font-weight: 700 !important;
        }
        """

    clean_css = textwrap.dedent(base_css).strip() + "\n" + textwrap.dedent(theme_css).strip()
    st.html(f"<style>\n{clean_css}\n</style>")


def render_sidebar():
    """Consistent clean sidebar across pages with Theme selector and user profile."""
    current_lang = st.session_state.get("lang", "en")
    active_theme = get_current_theme()

    with st.sidebar:
        st.markdown(f"## {text.T('app_title', current_lang)}")
        st.caption(text.T("app_subtitle", current_lang))
        st.divider()

        # Clean Global Theme Selector Dropdown in Sidebar
        current_display = THEMES.get(active_theme, "Classic Clean (Default)")
        theme_names = list(THEMES.values())
        theme_index = theme_names.index(current_display) if current_display in theme_names else 0

        st.selectbox(
            "🎨 " + ("Theme / ಥೀಮ್" if current_lang == "kn" else "Theme"),
            options=theme_names,
            index=theme_index,
            key="global_sidebar_theme_selector",
            on_change=_on_theme_dropdown_change
        )

        st.divider()

        user = st.session_state.get("user")
        if user:
            # User profile card rendered via clean HTML
            card_html = f"""
            <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); padding:12px; border-radius:10px; margin-bottom:14px;">
                <div style="font-size:0.75em; text-transform:uppercase; font-weight:700; letter-spacing:0.5px; opacity:0.8;">{text.T('sidebar_logged_in', current_lang)}</div>
                <div style="font-size:1.05em; font-weight:700;">👤 {user['name']}</div>
                <div style="font-size:0.85em; opacity:0.85;">📞 {user['phone']}</div>
            </div>
            """
            st.html(textwrap.dedent(card_html).strip())

            # Logout button
            if st.button(text.T("sidebar_logout", current_lang), use_container_width=True, type="secondary"):
                st.session_state["user"] = None
                st.rerun()
        else:
            login_hint_html = f"""
            <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); padding:12px; border-radius:10px; font-size:0.9em; margin-bottom:14px;">
                {text.T('sidebar_please_login', current_lang)}
            </div>
            """
            st.html(textwrap.dedent(login_hint_html).strip())

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(text.T("sidebar_helpline", current_lang))
        st.caption(text.T("sidebar_mithra", current_lang))


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
