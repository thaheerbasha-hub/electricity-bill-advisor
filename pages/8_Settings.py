"""
8_Settings.py · Settings & Preferences Page
Allows logged in users to customize Language, Theme, and Account info.
"""

import streamlit as st
import ui_common
import text

ui_common.apply_custom_css()
ui_common.render_sidebar()

user = st.session_state.get("user")
if not user:
    st.warning("Please log in first.")
    st.stop()

lang = st.session_state.get("lang", "en")


def _on_settings_lang_change():
    chosen = st.session_state.get("main_settings_lang")
    st.session_state["lang"] = "kn" if chosen == "ಕನ್ನಡ" else "en"


st.title(text.T("settings_sub", lang))
st.caption("Customize your display language, theme preferences, and account profile.")

st.markdown("<br>", unsafe_allow_html=True)

# 3 Sub-tabs inside Settings: Language, Theme, Account
sub_lang, sub_theme, sub_account = st.tabs([
    text.T("settings_tab_lang", lang),
    text.T("settings_tab_theme", lang),
    text.T("settings_tab_account", lang)
])

with sub_lang:
    st.subheader(text.T("settings_lang_label", lang))
    st.write(text.T("settings_lang_help", lang))
    st.radio(
        text.T("settings_lang_label", lang),
        options=["English", "ಕನ್ನಡ"],
        index=0 if lang == "en" else 1,
        horizontal=True,
        key="main_settings_lang",
        on_change=_on_settings_lang_change
    )

with sub_theme:
    st.subheader(text.T("theme_title", lang))
    st.write(text.T("theme_desc", lang))
    st.selectbox(
        text.T("theme_title", lang),
        options=[
            text.T("theme_default", lang),
            "Custom Theme 1 (Preview)",
            "Custom Theme 2 (Preview)"
        ],
        key="main_theme_selector"
    )
    st.info(text.T("theme_coming_soon", lang))

with sub_account:
    st.subheader(text.T("settings_account_sub", lang))
    c1, c2 = st.columns(2)
    c1.text_input("Name", value=user["name"], disabled=True)
    c2.text_input("Mobile Number", value=user["phone"], disabled=True)
