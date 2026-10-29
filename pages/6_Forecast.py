"""
6_Forecast.py · Next Month Bill Forecast & Mid-Month Test
Assigned to: AKSHAR
Features:
  - Projected bill range (low, expected, high)
  - Next month questions (away days, planned guests, summer flag)
  - Fuel shock simulator box (FPPCA variations)
  - Mid-month meter check: enter Day 15 reading to predict if you'll cross 200 units!
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

st.title("🔮 Next Month Forecast & Mid-Month Check")
st.caption("Plan your power consumption ahead, prevent fuel price shocks, and check your mid-month pace.")

bills = db.get_bills(user["id"])
if not bills:
    st.warning("Please add at least one bill in **My Bills** to calculate a forecast baseline.")
    st.stop()

latest = bills[-1]
normal_daily = latest["units"] / max(latest["days"], 1)

st.subheader("1 · Forecast Questions for Next Month")
c1, c2, c3 = st.columns(3)
with c1:
    away_next = st.number_input("Days you will be away next month", 0, 31, 0)
with c2:
    guests_next = st.number_input("Extra guests expected next month", 0, 20, 0)
with c3:
    summer_next = st.checkbox("Summer season (Mar to May)")

st.subheader("2 · Fuel Price Simulator")
fuel_next = st.number_input(
    "Simulated Fuel Surcharge / FPPCA (₹/unit)",
    min_value=0.0, max_value=3.0, value=float(latest["fuel_rs"]), step=0.05,
    help="Try ₹1.00 to see what an energy cost increase does to your bill even if you use the same power."
)

# Baseline projection
eff_days = (30 - away_next) + 0.3 * away_next
projected_units = normal_daily * eff_days * (1.15 if summer_next else 1.0) + (guests_next * 1.2 * 7)

low_u, mid_u, hi_u = projected_units * 0.9, projected_units, projected_units * 1.1

RATE = 5.80
FIXED_PER_KW = 150
TAX = 0.09
GJ_CAP = 200

def to_pay(u, f, free=latest.get("free_units"), kw=latest.get("load_kw", 2.0)):
    energy = u * RATE
    full = energy + kw * FIXED_PER_KW + u * f + energy * TAX
    if free is None or u > GJ_CAP:
        return full
    if u <= free:
        return 0.0
    return (u - free) * (RATE * (1 + TAX) + f)

b_lo = to_pay(low_u, fuel_next)
b_mid = to_pay(mid_u, fuel_next)
b_hi = to_pay(hi_u, fuel_next)

with st.container(border=True):
    st.markdown(f"### Estimated Bill: {ui_common.rupees(b_lo)} – {ui_common.rupees(b_hi)}")
    st.caption(f"Most likely **{ui_common.rupees(b_mid)}** (~{mid_u:.0f} units) assuming normal household patterns.")
    if latest.get("free_units") and hi_u > GJ_CAP:
        st.error(f"⚠️ **High Risk:** Your upper projection crosses 200 units ({hi_u:.0f} units). Aim to stay below {GJ_CAP/30:.1f} units/day to protect your Gruha Jyothi benefit!")

st.markdown("<br>", unsafe_allow_html=True)

# Mid-Month Check
with st.container(border=True):
    st.subheader("⚡ Mid-Month Pacing Check (Read Your Meter Today)")
    st.write("Check your meter around day 15 of your cycle to avoid sudden surprises:")
    
    col_a, col_b = st.columns(2)
    with col_a:
        cur_meter = st.number_input("Units used so far since last bill", min_value=0, max_value=2000, value=int(normal_daily * 15))
    with col_b:
        cur_days = st.number_input("Days elapsed since last bill", min_value=1, max_value=35, value=15)
        
    projected_month = (cur_meter / cur_days) * 30
    st.markdown(f"**Paced Monthly Consumption:** `{projected_month:.0f} units`")
    
    if latest.get("free_units") and projected_month > GJ_CAP:
        st.error(f"🚨 At this pace ({projected_month:.0f} units), you will exceed 200 units and **lose Gruha Jyothi**! "
                 f"Keep usage under `{(GJ_CAP - cur_meter) / max(30 - cur_days, 1):.1f} units/day` for the rest of the cycle.")
    else:
        st.success(f"✅ On track! At this pace ({projected_month:.0f} units), you are safely within your quota.")
