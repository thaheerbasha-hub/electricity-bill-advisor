"""
8_Settings.py · Settings & Preferences Page
Allows logged in users to switch languages and review preferences.
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
st.caption("Customize your display language and account preferences.")

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
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

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader(text.T("settings_account_sub", lang))
    c1, c2 = st.columns(2)
    c1.text_input("Name", value=user["name"], disabled=True)
    c2.text_input("Mobile Number", value=user["phone"], disabled=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader(text.T("settings_theme_sub", lang))
    st.caption(text.T("settings_theme_desc", lang))
