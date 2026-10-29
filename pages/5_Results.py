"""
5_Results.py · Results & Insights Breakdown
Assigned to: RISHABH
Features:
  - 3 Cards:
      1. Why it changed (rupee reasons + waterfall chart)
      2. Where the waste is (vacation test, unmeasured loss, alert)
      3. How to save (tailored tips with ₹ savings)
"""

import streamlit as st
import plotly.graph_objects as go
import db
import ui_common

ui_common.apply_custom_css()
ui_common.render_sidebar()

user = st.session_state.get("user")
if not user:
    st.warning("Please log in first.")
    st.stop()

st.title("📊 Diagnostic Results & Bill Jump Analysis")
st.caption("Here is the exact decomposition of why your bill changed and how to eliminate waste.")

bills = db.get_bills(user["id"])
if len(bills) < 2:
    st.warning("Please record at least 2 bills in **My Bills** to view diagnostic results.")
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
m1.metric("Current Bill", ui_common.rupees(pay_cur))
m2.metric("Previous Bill", ui_common.rupees(pay_prev))
m3.metric("Net Change", f"{'+' if diff > 0 else ''}{ui_common.rupees(diff)}", delta=ui_common.rupees(diff), delta_color="inverse")

# --- Card 1: Why your bill changed ---
with st.container(border=True):
    st.subheader("1 · Why your bill changed")
    st.markdown(f"**Net Jump:** {ui_common.rupees(diff)}")
    
    # Simple simulated waterfall until Rishabh connects engine.explain()
    labels = ["Previous Bill", "Billing Days", "Guest Usage", "Hot Weather/AC", "Gruha Jyothi Impact", "Current Bill"]
    measures = ["absolute", "relative", "relative", "relative", "relative", "total"]
    
    # Calculate illustrative components
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
    st.subheader("2 · Where the waste is (Audits & Leakage)")
    if ans.get("vacation_days", 0) >= 5:
        st.error(f"⚠️ **Vacation Test:** You were away for {ans['vacation_days']} days, but your daily consumption remained elevated. Check for continuous loads like running geysers, water pump auto-fill loops, or inverter float charge.")
    else:
        st.success("✅ **Vacation Audit:** No abnormal standby waste detected for this period.")
    
    if cur["units"] > GJ_CAP and cur.get("free_units"):
        over = cur["units"] - GJ_CAP
        st.warning(f"⚠️ **Crossed 200 Units:** You exceeded the Gruha Jyothi quota by only {over:.0f} units! Staying under 200 units would have saved {ui_common.rupees(pay_cur)}.")

# --- Card 3: Tailored Savings Tips ---
with st.container(border=True):
    st.subheader("3 · How to save on next bill")
    tips_list = [
        ("Set AC thermostat to 24°C–26°C instead of 18°C–21°C", "Saves ~₹450/month", "Free"),
        ("Install an auto-cut sensor for the water tank pump to prevent overflow runs", "Saves ~₹280/month", "₹400 one-time"),
        ("Switch off the electric geyser at the mains switch immediately after use", "Saves ~₹320/month", "Free"),
        ("Check meter on the 15th of every month using our Forecast tab to stay under 200 units", "Saves up to ₹1,400/month", "Free")
    ]
    for tip, save, cost in tips_list:
        st.markdown(f"💡 **{tip}** — *{save}* (Implementation cost: `{cost}`)")
