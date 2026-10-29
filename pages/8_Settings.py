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


def _on_settings_theme_change():
    chosen_label = st.session_state.get("main_settings_theme_selector")
    chosen_key = ui_common.THEME_DISPLAY_TO_KEY.get(chosen_label, "classic")
    st.session_state["theme"] = chosen_key
    st.query_params["theme"] = chosen_key


st.title(text.T("settings_sub", lang))
st.caption("Customize your display language, theme preferences, and account profile." if lang == "en" else "ನಿಮ್ಮ ಭಾಷೆ, ಥೀಮ್ ಆದ್ಯತೆಗಳು ಮತ್ತು ಖಾತೆಯ ವಿವರಗಳನ್ನು ಕಸ್ಟಮೈಸ್ ಮಾಡಿ.")

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

    current_theme_key = ui_common.get_current_theme()
    current_theme_label = ui_common.THEMES.get(current_theme_key, "Classic Clean (Default)")
    theme_options = list(ui_common.THEMES.values())
    curr_idx = theme_options.index(current_theme_label) if current_theme_label in theme_options else 0

    st.selectbox(
        text.T("theme_title", lang),
        options=theme_options,
        index=curr_idx,
        key="main_settings_theme_selector",
        on_change=_on_settings_theme_change
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### " + ("Theme Previews & Features" if lang == "en" else "ಥೀಮ್ ವಿವರಣೆಗಳು"))
    
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.markdown("""
        **1. Classic Clean (Default)**  
        *Original professional layout with crisp white cards, slate text, and emerald accents.*
        
        **2. Neon Glass**  
        *Futuristic cosmic dark glassmorphism with frosted blur, glowing cyan/purple borders, and glowing metric pills.*
        
        **3. Soft Clay**  
        *Playful 3D puffed pastel candy elements with rounded soft clay shadows and powder blue canvas.*
        """)
    with t_c2:
        st.markdown("""
        **4. Cozy Wool**  
        *Tactile warm tweed canvas with stitched dashed borders, fabric patch cards, and stitched forest-green badges.*
        
        **5. Smooth Tactile**  
        *Monochromatic soft-UI neumorphic design with extruded surface cards and sunken inset input wells.*
        """)

with sub_account:
    st.subheader(text.T("settings_account_sub", lang))
    c1, c2 = st.columns(2)
    c1.text_input("Name", value=user["name"], disabled=True)
    c2.text_input("Mobile Number", value=user["phone"], disabled=True)
