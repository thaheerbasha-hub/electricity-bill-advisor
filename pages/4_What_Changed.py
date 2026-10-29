"""
4_What_Changed.py · What Changed This Month?
Assigned to: RISHABH
Features:
  - Questions for the latest bill (vacations, guests, heat/AC, geyser, motor, new items, festival lights, power cuts)
  - Answers stored in st.session_state["answers"] for Results page
  - Fully bilingual (English / Kannada)
"""

import streamlit as st
import db
import ui_common
import text

ui_common.apply_custom_css()
ui_common.render_sidebar()

user = st.session_state.get("user")
if not user:
    st.warning("Please log in first.")
    st.stop()

lang = st.session_state.get("lang", "en")

st.title(text.T("changed_title", lang))
st.caption(text.T("changed_caption", lang))

bills = db.get_bills(user["id"])
if len(bills) < 2:
    st.warning("You need at least 2 bills saved to diagnose what changed. Please add another bill in **My Bills**." if lang == "en" else "ಬಿಲ್ ಬದಲಾವಣೆ ತಿಳಿಯಲು ಕನಿಷ್ಠ 2 ಬಿಲ್‌ಗಳು ಬೇಕು. ದಯವಿಟ್ಟು **ನನ್ನ ಬಿಲ್‌ಗಳು** ಪುಟದಲ್ಲಿ ಇನ್ನೊಂದು ಬಿಲ್ ಸೇರಿಸಿ.")
    if st.button("Go to My Bills →" if lang == "en" else "ನನ್ನ ಬಿಲ್‌ಗಳಿಗೆ ಹೋಗಿ →"):
        st.switch_page("pages/3_My_Bills.py")
    st.stop()

cur = bills[-1]
prev = bills[-2]

st.info(f"Comparing current bill (**{cur['month']}**: {cur['units']:.0f} units, {cur['days']} days) vs previous bill (**{prev['month']}**: {prev['units']:.0f} units, {prev['days']} days)." if lang == "en" else f"ಪ್ರಸ್ತುತ ಬಿಲ್ (**{cur['month']}**: {cur['units']:.0f} ಯೂನಿಟ್, {cur['days']} ದಿನ) vs ಹಿಂದಿನ ಬಿಲ್ (**{prev['month']}**: {prev['units']:.0f} ಯೂನಿಟ್, {prev['days']} ದಿನ) ಹೋಲಿಕೆ.")

NEW_ITEMS = ["AC", "Geyser", "Fridge", "Washing machine", "E-scooter / EV charging", "Induction stove", "Something else"]

current_ans = st.session_state.get("answers", {
    "vacation_days": 0, "guests_people": 0, "guests_days": 0,
    "heat": False, "geyser": False, "home_more": False, "pump": False,
    "new_items": [], "festival_lights": False, "power_cuts": False
})

with st.form("what_changed_form"):
    q1, q2 = st.columns(2)
    with q1:
        st.subheader(text.T("changed_travel_sub", lang))
        vacation = st.number_input(text.T("changed_vacation", lang), 0, 45, current_ans.get("vacation_days", 0))
        guests_people = st.number_input(text.T("changed_guests", lang), 0, 25, current_ans.get("guests_people", 0))
        guests_days = st.number_input(text.T("changed_guest_days", lang), 0, 45, current_ans.get("guests_days", 0)) if guests_people > 0 else 0
        
        st.subheader(text.T("changed_weather_sub", lang))
        heat = st.checkbox(text.T("changed_heat", lang), current_ans.get("heat", False))
        geyser = st.checkbox(text.T("changed_geyser", lang), current_ans.get("geyser", False))

    with q2:
        st.subheader(text.T("changed_habits_sub", lang))
        home_more = st.checkbox(text.T("changed_home_more", lang), current_ans.get("home_more", False))
        pump = st.checkbox(text.T("changed_pump", lang), current_ans.get("pump", False))
        festival_lights = st.checkbox(text.T("changed_fest", lang), current_ans.get("festival_lights", False))
        power_cuts = st.checkbox(text.T("changed_power_cuts", lang), current_ans.get("power_cuts", False))
        new_items = st.multiselect(text.T("changed_new_items", lang), NEW_ITEMS, default=current_ans.get("new_items", []))

    saved = st.form_submit_button(text.T("changed_submit_btn", lang), type="primary", use_container_width=True)
    if saved:
        st.session_state["answers"] = {
            "vacation_days": vacation,
            "guests_people": guests_people,
            "guests_days": guests_days,
            "heat": heat,
            "geyser": geyser,
            "home_more": home_more,
            "pump": pump,
            "new_items": new_items,
            "festival_lights": festival_lights,
            "power_cuts": power_cuts
        }
        st.success("Answers saved! Heading to Results..." if lang == "en" else "ಉತ್ತರಗಳನ್ನು ಉಳಿಸಲಾಗಿದೆ! ಫಲಿತಾಂಶ ಪುಟಕ್ಕೆ ಹೋಗಲಾಗುತ್ತಿದೆ...")
        st.switch_page("pages/5_Results.py")
