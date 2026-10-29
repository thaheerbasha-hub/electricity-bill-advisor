"""
1_Login.py · Power Bill Coach Login & Sign Up
Handles user authentication with phone + Security PIN.
Stores data locally in SQLite with hashed PINs.
Supports full instantaneous Kannada & English translation.
"""

import streamlit as st
import db
import ui_common
import text

ui_common.apply_custom_css()
ui_common.render_sidebar()

lang = st.session_state.get("lang", "en")

# Header & Tagline
st.title(text.T("app_title", lang))
st.markdown(f"### {text.T('tagline', lang)}")
st.caption(text.T("no_passwords", lang))

st.markdown("<br>", unsafe_allow_html=True)

# Main Login / Sign Up container
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    # Instant Demo Card for Hackathon Judges
    with st.container(border=True):
        st.markdown(f"#### {text.T('judge_card_title', lang)}")
        st.write(text.T("judge_card_desc", lang))
        if st.button(text.T("judge_btn", lang), type="primary", use_container_width=True):
            user = db.check_login("9876543210", "1234")
            if user:
                st.session_state["user"] = user
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs([text.T("tab_login", lang), text.T("tab_signup", lang)])

    # --- TAB 1: LOG IN ---
    with tab_login:
        st.subheader(text.T("login_sub", lang))
        phone_in = st.text_input(text.T("phone_label", lang), max_chars=10, placeholder=text.T("phone_placeholder", lang), key="login_phone")
        pin_in = st.text_input(text.T("pin_label", lang), type="password", placeholder=text.T("pin_placeholder", lang), key="login_pin")
        
        # In-page Language Selector with immediate rerun
        lang_sel = st.selectbox(
            text.T("sidebar_lang_label", lang),
            ["English", "ಕನ್ನಡ"],
            index=0 if lang == "en" else 1,
            key="login_lang_picker"
        )
        selected_lang = "en" if lang_sel == "English" else "kn"
        if selected_lang != lang:
            st.session_state["lang"] = selected_lang
            st.rerun()

        if st.button(text.T("btn_login", lang), type="primary", use_container_width=True, key="btn_login"):
            if not phone_in or len(phone_in) < 10:
                st.error(text.T("err_phone", lang))
            elif not pin_in:
                st.error(text.T("err_pin", lang))
            else:
                user = db.check_login(phone_in, pin_in)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error(text.T("err_invalid_login", lang))

    # --- TAB 2: SIGN UP ---
    with tab_signup:
        st.subheader(text.T("signup_sub", lang))
        st.caption(text.T("signup_caption", lang))
        new_name = st.text_input(text.T("name_label", lang), placeholder=text.T("name_placeholder", lang), key="signup_name")
        new_phone = st.text_input(text.T("phone_label", lang), max_chars=10, placeholder=text.T("phone_placeholder", lang), key="signup_phone")
        new_pin = st.text_input(text.T("pin_label", lang), type="password", placeholder=text.T("pin_placeholder", lang), key="signup_pin")
        confirm_pin = st.text_input(text.T("pin_confirm_label", lang), type="password", placeholder=text.T("pin_placeholder", lang), key="signup_confirm_pin")

        if st.button(text.T("btn_signup", lang), type="primary", use_container_width=True, key="btn_signup"):
            if not new_name.strip():
                st.error(text.T("err_name", lang))
            elif len(new_phone.strip()) < 10 or not new_phone.strip().isdigit():
                st.error(text.T("err_phone", lang))
            elif not new_pin:
                st.error(text.T("err_pin", lang))
            elif new_pin != confirm_pin:
                st.error(text.T("err_pin_match", lang))
            else:
                success = db.add_user(new_name, new_phone, new_pin)
                if success:
                    user = db.check_login(new_phone, new_pin)
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error(text.T("err_user_exists", lang))
