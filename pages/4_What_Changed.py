"""
4_What_Changed.py · What Changed This Month?
Assigned to: RISHABH
Features:
  - Questions for the latest bill (vacations, guests, heat/AC, geyser, motor, new items, festival lights, power cuts)
  - Answers stored in st.session_state["answers"] for Results page
"""

import streamlit as st
import db
import ui_common

ui_common.apply_custom_css()
ui_common.render_sidebar()

user = st.session_state.get("user")
if not user:
    st.warning("Please log in first.")
    st.stop()

st.title("🔍 What Changed This Month?")
st.caption("Tell us what was different in your household during this billing cycle. No technical wattage questions!")

bills = db.get_bills(user["id"])
if len(bills) < 2:
    st.warning("You need at least 2 bills saved to diagnose what changed. Please add another bill in **My Bills**.")
    if st.button("Go to My Bills →"):
        st.switch_page("pages/3_My_Bills.py")
    st.stop()

cur = bills[-1]
prev = bills[-2]

st.info(f"Comparing current bill (**{cur['month']}**: {cur['units']:.0f} units, {cur['days']} days) vs previous bill (**{prev['month']}**: {prev['units']:.0f} units, {prev['days']} days).")

NEW_ITEMS = ["AC", "Geyser", "Fridge", "Washing machine", "E-scooter / EV charging", "Induction stove", "Something else"]

# Initialize or retrieve answers from session state
current_ans = st.session_state.get("answers", {
    "vacation_days": 0,
    "guests_people": 0,
    "guests_days": 0,
    "heat": False,
    "geyser": False,
    "home_more": False,
    "pump": False,
    "new_items": [],
    "festival_lights": False,
    "power_cuts": False
})

with st.form("what_changed_form"):
    q1, q2 = st.columns(2)
    with q1:
        st.subheader("🏖️ Travel & Guests")
        vacation = st.number_input("Days nobody was home (vacation / out of station)", 0, 45, current_ans.get("vacation_days", 0))
        guests_people = st.number_input("How many guests stayed over? (0 if none)", 0, 25, current_ans.get("guests_people", 0))
        guests_days = st.number_input("For how many days did guests stay?", 0, 45, current_ans.get("guests_days", 0)) if guests_people > 0 else 0
        
        st.subheader("🌡️ Weather & Seasons")
        heat = st.checkbox("It was hot / summer, and we used AC / cooler / fans more", current_ans.get("heat", False))
        geyser = st.checkbox("It was rainy / cold, and we ran the geyser / water heater more", current_ans.get("geyser", False))

    with q2:
        st.subheader("🏠 Home Habits & Appliances")
        home_more = st.checkbox("More people stayed home during the daytime (holidays / WFH)", current_ans.get("home_more", False))
        pump = st.checkbox("Water motor / borehole pump ran more often (water shortage / overflow)", current_ans.get("pump", False))
        festival_lights = st.checkbox("Put up decorative festival lighting (Dasara / Diwali / Ramadan / Christmas)", current_ans.get("festival_lights", False))
        power_cuts = st.checkbox("Frequent power cuts / inverter ran extra charge cycles", current_ans.get("power_cuts", False))
        new_items = st.multiselect("Did you purchase or start using any new appliances?", NEW_ITEMS, default=current_ans.get("new_items", []))

    saved = st.form_submit_button("Analyze My Bill Jump →", type="primary", use_container_width=True)
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
        st.success("Answers saved! Heading to Results...")
        st.switch_page("pages/5_Results.py")
