"""
ui_common.py · Shared UI styling, layout, and sidebar across all pages
"""

import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
    /* Global modern clean style */
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers & Brand */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
    }
    
    /* Card Container */
    .pbc-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    /* Metric Highlights */
    .pbc-metric-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        border-left: 5px solid #10b981;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    
    /* Button primary */
    .stButton>button[kind="primary"] {
        background-color: #059669;
        border-color: #059669;
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Alert badges */
    .badge-danger {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85em;
    }
    .badge-success {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85em;
    }
    .badge-warn {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85em;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Consistent sidebar across every page: user status, language, logout, helpline"""
    with st.sidebar:
        # App logo & title
        st.markdown("### ⚡ Power Bill Coach")
        st.caption("Karnataka · BESCOM Domestic Advisor")
        st.divider()

        user = st.session_state.get("user")
        if user:
            # User profile card
            st.markdown(f"""
            <div style="background:#f1f5f9; padding:12px; border-radius:10px; margin-bottom:12px;">
                <div style="font-size:0.8em; color:#64748b; text-transform:uppercase; font-weight:700;">Logged In As</div>
                <div style="font-size:1.1em; font-weight:700; color:#0f172a;">👤 {user['name']}</div>
                <div style="font-size:0.85em; color:#475569;">📞 {user['phone']}</div>
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
            st.info("🔐 Please log in to view your household bills and insights.")

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.caption("☎️ **BESCOM Helpline**: 1912")
        st.caption("📱 **BESCOM Mithra App** for official meter complaints")


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
