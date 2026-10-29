"""
1_Login.py · Power Bill Coach Login & Sign Up
Handles user authentication with phone + 4-digit PIN.
Stores data locally in SQLite with hashed PINs.
Never asks for BESCOM credentials.
"""

import streamlit as st
import db
import ui_common

ui_common.apply_custom_css()
ui_common.render_sidebar()

lang = st.session_state.get("lang", "en")

# Header
st.title("⚡ Power Bill Coach · Karnataka")
if lang == "kn":
    st.markdown("### ಸುಸ್ವಾಗತ! ನಿಮ್ಮ ವಿದ್ಯುತ್ ಬಿಲ್ ಅನ್ನು ಸುಲಭವಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ.")
    st.caption("ಯಾವುದೇ ಸಂಕೀರ್ಣ ಪದಗಳಿಲ್ಲ. ಕೇವಲ ಸರಳ ಪ್ರಶ್ನೆಗಳು. ನಾವು ಬೆಸ್ಕಾಂ ಪಾಸ್‌ವರ್ಡ್‌ಗಳನ್ನು ಎಂದಿಗೂ ಕೇಳುವುದಿಲ್ಲ.")
else:
    st.markdown("### Welcome! Understand and save on your electricity bills.")
    st.caption("No watts, no appliance lists. Just your bill numbers and simple questions. We never ask for BESCOM passwords.")

st.markdown("<br>", unsafe_allow_html=True)

# Main Login / Sign Up container
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    # Instant Demo Card for Hackathon Judges
    with st.container(border=True):
        st.markdown("#### 🚀 Quick Access for Judges & Reviewers")
        st.write("Skip typing and test the full app immediately with 6 pre-loaded sample bills:")
        if st.button("⚡ Launch Instant Demo Account", type="primary", use_container_width=True):
            user = db.check_login("9876543210", "1234")
            if user:
                st.session_state["user"] = user
                st.success("Logged in as Demo User!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔑 Log In", "📝 Create Account"])

    # --- TAB 1: LOG IN ---
    with tab_login:
        st.subheader("Log in to your account")
        phone_in = st.text_input("Mobile Number (10 digits)", max_chars=10, placeholder="9876543210", key="login_phone")
        pin_in = st.text_input("4-digit Security PIN", type="password", max_chars=4, placeholder="••••", key="login_pin")
        
        # Language preference
        lang_sel = st.selectbox("Preferred Language / ಭಾಷೆ", ["English", "ಕನ್ನಡ"], index=0 if lang == "en" else 1, key="login_lang_picker")
        st.session_state["lang"] = "en" if lang_sel == "English" else "kn"

        if st.button("Log In", type="primary", use_container_width=True, key="btn_login"):
            if not phone_in or len(phone_in) < 10:
                st.error("Please enter a valid 10-digit mobile number.")
            elif not pin_in or len(pin_in) != 4:
                st.error("Please enter your 4-digit PIN.")
            else:
                user = db.check_login(phone_in, pin_in)
                if user:
                    st.session_state["user"] = user
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Incorrect mobile number or PIN. Please try again or create an account.")

    # --- TAB 2: SIGN UP ---
    with tab_signup:
        st.subheader("Create a new account")
        st.caption("Your details are stored strictly in a local database. No BESCOM passwords needed.")
        new_name = st.text_input("Full Name / Household Name", placeholder="e.g. Ramesh Kumar", key="signup_name")
        new_phone = st.text_input("Mobile Number (10 digits)", max_chars=10, placeholder="9876543210", key="signup_phone")
        new_pin = st.text_input("Choose a 4-digit PIN", type="password", max_chars=4, placeholder="••••", key="signup_pin")
        confirm_pin = st.text_input("Confirm 4-digit PIN", type="password", max_chars=4, placeholder="••••", key="signup_confirm_pin")

        if st.button("Create Account", type="primary", use_container_width=True, key="btn_signup"):
            if not new_name.strip():
                st.error("Please enter your name.")
            elif len(new_phone.strip()) < 10 or not new_phone.strip().isdigit():
                st.error("Please enter a valid 10-digit mobile number.")
            elif len(new_pin) != 4 or not new_pin.isdigit():
                st.error("PIN must be exactly 4 digits.")
            elif new_pin != confirm_pin:
                st.error("The PINs do not match. Please re-enter.")
            else:
                success = db.add_user(new_name, new_phone, new_pin)
                if success:
                    st.success("Account created successfully! Logging you in...")
                    user = db.check_login(new_phone, new_pin)
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("An account with this mobile number already exists. Please log in.")
