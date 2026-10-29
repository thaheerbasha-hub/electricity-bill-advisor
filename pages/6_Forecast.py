"""
6_Forecast.py · Next Month Bill Forecast & Mid-Month Test
Assigned to: AKSHAR
Features:
  - Projected bill range (low, expected, high)
  - Next month questions (away days, planned guests, summer flag)
  - Fuel shock simulator box (FPPCA variations)
  - Mid-month meter check: enter Day 15 reading to predict if you'll cross 200 units!
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

st.title(text.T("forecast_title", lang))
st.caption(text.T("forecast_caption", lang))

bills = db.get_bills(user["id"])
if not bills:
    st.warning("Please add at least one bill in **My Bills** to calculate a forecast baseline." if lang == "en" else "ಮುನ್ಸೂಚನೆ ಲೆಕ್ಕಹಾಕಲು ದಯವಿಟ್ಟು **ನನ್ನ ಬಿಲ್‌ಗಳು** ಪುಟದಲ್ಲಿ ಕನಿಷ್ಠ 1 ಬಿಲ್ ಸೇರಿಸಿ.")
    st.stop()

latest = bills[-1]
normal_daily = latest["units"] / max(latest["days"], 1)

st.subheader(text.T("forecast_q_sub", lang))
c1, c2, c3 = st.columns(3)
with c1:
    away_next = st.number_input(text.T("forecast_away", lang), 0, 31, 0)
with c2:
    guests_next = st.number_input(text.T("forecast_guests", lang), 0, 20, 0)
with c3:
    summer_next = st.checkbox(text.T("forecast_summer", lang))

st.subheader(text.T("forecast_fuel_sub", lang))
fuel_next = st.number_input(
    text.T("forecast_fuel_label", lang),
    min_value=0.0, max_value=3.0, value=float(latest["fuel_rs"]), step=0.05,
    help=text.T("forecast_fuel_help", lang)
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
    st.markdown(f"### {text.T('forecast_est_bill', lang)} {ui_common.rupees(b_lo)} – {ui_common.rupees(b_hi)}")
    st.caption(f"{text.T('forecast_likely', lang)}: **{ui_common.rupees(b_mid)}** (~{mid_u:.0f} units)")
    if latest.get("free_units") and hi_u > GJ_CAP:
        st.error(text.T("forecast_risk_high", lang))

st.markdown("<br>", unsafe_allow_html=True)

# Mid-Month Check
with st.container(border=True):
    st.subheader(text.T("forecast_mid_sub", lang))
    st.write(text.T("forecast_mid_desc", lang))
    
    col_a, col_b = st.columns(2)
    with col_a:
        cur_meter = st.number_input(text.T("forecast_units_used", lang), min_value=0, max_value=2000, value=int(normal_daily * 15))
    with col_b:
        cur_days = st.number_input(text.T("forecast_days_passed", lang), min_value=1, max_value=35, value=15)
        
    projected_month = (cur_meter / cur_days) * 30
    st.markdown(f"**{text.T('forecast_paced_usage', lang)}** `{projected_month:.0f} units`")
    
    if latest.get("free_units") and projected_month > GJ_CAP:
        st.error(text.T("forecast_lose_gj", lang))
    else:
        st.success(text.T("forecast_on_track", lang))
