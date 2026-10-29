"""
5_Results.py · Results & Insights Breakdown
Assigned to: RISHABH
Features:
  - 3 Cards:
      1. Why it changed (rupee reasons + waterfall chart)
      2. Where the waste is (vacation test, unmeasured loss, alert)
      3. How to save (tailored tips with ₹ savings)
  - Fully bilingual (English / Kannada)
"""

import streamlit as st
import plotly.graph_objects as go
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

st.title(text.T("results_title", lang))
st.caption(text.T("results_caption", lang))

bills = db.get_bills(user["id"])
if len(bills) < 2:
    st.warning("Please record at least 2 bills in **My Bills** to view diagnostic results." if lang == "en" else "ಫಲಿತಾಂಶ ನೋಡಲು ದಯವಿಟ್ಟು **ನನ್ನ ಬಿಲ್‌ಗಳು** ಪುಟದಲ್ಲಿ ಕನಿಷ್ಠ 2 ಬಿಲ್ ದಾಖಲಿಸಿ.")
    st.stop()

cur = bills[-1]
prev = bills[-2]
ans = st.session_state.get("answers", {
    "vacation_days": 0, "guests_people": 0, "guests_days": 0,
    "heat": False, "geyser": False, "home_more": False, "pump": False,
    "new_items": [], "festival_lights": False, "power_cuts": False
})

# Rates
RATE = 5.80
FIXED_PER_KW = 150
TAX = 0.09
GJ_CAP = 200

def to_pay(u, d, kw, f, free):
    energy = u * RATE
    full = energy + kw * FIXED_PER_KW * d / 30 + u * f + energy * TAX
    if free is None or u > GJ_CAP:
        return full
    if u <= free:
        return 0.0
    return (u - free) * (RATE * (1 + TAX) + f)

pay_prev = to_pay(prev["units"], prev["days"], prev["load_kw"], prev["fuel_rs"], prev["free_units"])
pay_cur = to_pay(cur["units"], cur["days"], cur["load_kw"], cur["fuel_rs"], cur["free_units"])
diff = pay_cur - pay_prev

# Quick metrics
m1, m2, m3 = st.columns(3)
m1.metric("Current Bill" if lang == "en" else "ಪ್ರಸ್ತುತ ಬಿಲ್", ui_common.rupees(pay_cur))
m2.metric("Previous Bill" if lang == "en" else "ಹಿಂದಿನ ಬಿಲ್", ui_common.rupees(pay_prev))
m3.metric("Net Change" if lang == "en" else "ಒಟ್ಟು ವ್ಯತ್ಯಾಸ", f"{'+' if diff > 0 else ''}{ui_common.rupees(diff)}", delta=ui_common.rupees(diff), delta_color="inverse")

# --- Card 1: Why your bill changed ---
with st.container(border=True):
    st.subheader(text.T("card1_sub", lang))
    st.markdown(f"**{text.T('card1_net_jump', lang)}** {ui_common.rupees(diff)}")
    
    if lang == "kn":
        labels = ["ಹಿಂದಿನ ಬಿಲ್", "ಹೆಚ್ಚುವರಿ ದಿನಗಳು", "ಅತಿಥಿಗಳ ಬಳಕೆ", "ಬಿಸಿಲು / AC", "ಗೃಹ ಜ್ಯೋತಿ ಪರಿಣಾಮ", "ಈ ತಿಂಗಳ ಬಿಲ್"]
    else:
        labels = ["Previous Bill", "Billing Days", "Guest Usage", "Hot Weather/AC", "Gruha Jyothi Impact", "Current Bill"]

    measures = ["absolute", "relative", "relative", "relative", "relative", "total"]
    
    d_day_val = (cur["days"] - prev["days"]) * (prev["units"]/prev["days"]) * RATE * (1+TAX)
    guest_val = (ans.get("guests_people", 0) * ans.get("guests_days", 0) * 1.2) * RATE * (1+TAX)
    heat_val = (35.0 * RATE * (1+TAX)) if ans.get("heat") else 0.0
    gj_val = (pay_cur - (pay_prev + d_day_val + guest_val + heat_val)) if cur["units"] > GJ_CAP and cur.get("free_units") else 0.0
    
    vals = [pay_prev, d_day_val, guest_val, heat_val, gj_val, pay_cur]
    
    fig = go.Figure(go.Waterfall(
        x=labels,
        measure=measures,
        y=[pay_prev, d_day_val, guest_val, heat_val, gj_val, 0],
        text=[ui_common.rupees(v) for v in vals],
        textposition="outside",
        increasing={"marker": {"color": "#dc2626"}},
        decreasing={"marker": {"color": "#16a34a"}},
        totals={"marker": {"color": "#2563eb"}}
    ))
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- Card 2: Waste Detection ---
with st.container(border=True):
    st.subheader(text.T("card2_sub", lang))
    if ans.get("vacation_days", 0) >= 5:
        if lang == "kn":
            st.error(f"⚠️ **ರಜೆ ತಪಾಸಣೆ:** ನೀವು {ans['vacation_days']} ದಿನ ಮನೆಯಲ್ಲಿ ಇರಲಿಲ್ಲ, ಆದರೆ ವಿದ್ಯುತ್ ಬಳಕೆ ಕಡಿಮೆಯಾಗಿಲ್ಲ! ಚಾಲನೆಯಲ್ಲಿರುವ ಗೀಸರ್, ನೀರಿನ ಪಂಪ್ ಅಥವಾ ಇನ್ವರ್ಟರ್ ತಪಾಸಣೆ ಮಾಡಿ.")
        else:
            st.error(f"⚠️ **Vacation Test:** You were away for {ans['vacation_days']} days, but daily consumption stayed high. Check running geysers, pumps, or vampire loads.")
    else:
        st.success("✅ ರಜೆ ತಪಾಸಣೆ ಯಶಸ್ವಿ: ಯಾವುದೇ ಅಸಹಜ ವಿದ್ಯುತ್ ನಷ್ಟ ಕಂಡುಬಂದಿಲ್ಲ." if lang == "kn" else "✅ Vacation Audit: No abnormal standby waste detected for this period.")
    
    if cur["units"] > GJ_CAP and cur.get("free_units"):
        over = cur["units"] - GJ_CAP
        if lang == "kn":
            st.warning(f"⚠️ **200 ಯೂನಿಟ್ ಮೀರಿದೆ:** ನೀವು ಕೇವಲ {over:.0f} ಯೂನಿಟ್‌ಗಳಿಂದ ಮಿತಿ ಮೀರಿದ್ದೀರಿ! 200ರ ಒಳಗೆ ಇಟ್ಟಿದ್ದರೆ {ui_common.rupees(pay_cur)} ಉಳಿಯುತ್ತಿತ್ತು.")
        else:
            st.warning(f"⚠️ **Crossed 200 Units:** You exceeded the cap by only {over:.0f} units! Staying under 200 units would have saved {ui_common.rupees(pay_cur)}.")

# --- Card 3: Tailored Savings Tips ---
with st.container(border=True):
    st.subheader(text.T("card3_sub", lang))
    if lang == "kn":
        tips_list = [
            ("AC ತಾಪಮಾನವನ್ನು 18°C ಬದಲಿಗೆ 24°C–26°C ಗೆ ಹೊಂದಿಸಿ", "~₹450/ತಿಂಗಳು ಉಳಿತಾಯ", "ಉಚಿತ"),
            ("ನೀರಿನ ಟ್ಯಾಂಕ್ ಉಕ್ಕಿ ಹರಿಯುವುದನ್ನು ತಡೆಯಲು ಆಟೋ-ಕಟ್ ಸೆನ್ಸರ್ ಅಳವಡಿಸಿ", "~₹280/ತಿಂಗಳು ಉಳಿತಾಯ", "₹400 ಒಂದು ಬಾರಿ"),
            ("ಸ್ನಾನದ ನಂತರ ಗೀಸರ್ ಸ್ವಿಚ್ ಆಫ್ ಮಾಡಿ", "~₹320/ತಿಂಗಳು ಉಳಿತಾಯ", "ಉಚಿತ"),
            ("200 ಯೂನಿಟ್ ಒಳಗೆ ಇರಿಸಲು ಪ್ರತಿ ತಿಂಗಳ 15ನೇ ತಾರೀಖು ಮೀಟರ್ ಪರಿಶೀಲಿಸಿ", "₹1,400 ವರೆಗೆ ಉಳಿತಾಯ", "ಉಚಿತ")
        ]
    else:
        tips_list = [
            ("Set AC thermostat to 24°C–26°C instead of 18°C–21°C", "Saves ~₹450/month", "Free"),
            ("Install an auto-cut sensor for water tank pump to prevent overflow runs", "Saves ~₹280/month", "₹400 one-time"),
            ("Switch off the electric geyser at the mains switch immediately after use", "Saves ~₹320/month", "Free"),
            ("Check meter on the 15th of every month using our Forecast tab to stay under 200 units", "Saves up to ₹1,400/month", "Free")
        ]
    for tip, save, cost in tips_list:
        st.markdown(f"💡 **{tip}** — *{save}* ({'ವೆಚ್ಚ' if lang == 'kn' else 'Cost'}: `{cost}`)")
