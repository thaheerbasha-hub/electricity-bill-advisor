"""
6_Forecast.py · Next Month Bill Forecast & Mid-Month Test
Assigned to: AKSHAR
Features:
  - Projected bill range (low, expected, high) in RUPEES
  - "Rates vs you" line breaking down tariff/fuel (not your fault) vs usage
  - Fuel shock simulator box with Strait of Hormuz context
  - Dynamic mid-month meter check with variable billing cycle days (25-35)
  - Scaling fixed charges with billing days
  - Fully bilingual (English / Kannada)
"""

import streamlit as st
import db
import ui_common
import text

from engine import (
    GJ_CAP,
    AWAY_SHARE,
    to_pay,
    normal_use,
    fuel_shock,
)

ui_common.apply_custom_css()
ui_common.render_sidebar()

# lang must be defined before any text.T() call, including inside login guard
lang = st.session_state.get("lang", "en")

user = st.session_state.get("user")
if not user:
    c_w, c_b = st.columns([3, 1])
    with c_w:
        st.warning(text.T("sidebar_please_login", lang))
    with c_b:
        if st.button("Preview with Demo Profile", key="demo_login_forecast"):
            st.session_state["user"] = {"id": 1, "name": "Ramesh Kumar (Demo)", "phone": "9876543210"}
            st.rerun()
    st.stop()

st.title(text.T("forecast_title", lang))
st.caption(text.T("forecast_caption", lang))

bills = db.get_bills(user["id"])
if not bills:
    st.warning(
        "Please add at least one bill in **My Bills** to calculate a forecast baseline."
        if lang == "en"
        else "ಮುನ್ಸೂಚನೆ ಲೆಕ್ಕಹಾಕಲು ದಯವಿಟ್ಟು **ನನ್ನ ಬಿಲ್‌ಗಳು** ಪುಟದಲ್ಲಿ ಕನಿಷ್ಠ 1 ಬಿಲ್ ಸೇರಿಸಿ."
    )
    st.stop()

latest = bills[-1]
normal_daily = float(normal_use(bills))
kw = float(latest.get("load_kw", 2.0))
free = latest.get("free_units")
last_days = int(latest.get("days", 30))

# fuel_per_unit is always the per-unit rate from db.get_bills()
# fuel_rs is set as an alias for the same value (both are per-unit, NOT totals)
# Never divide by units here — that would make it ~0
last_fuel_rate = round(float(latest.get("fuel_per_unit") or latest.get("fuel_rs") or 0.0), 2)

# 1. Inputs refining next month forecast
st.subheader(text.T("forecast_q_sub", lang))
c1, c2, c3 = st.columns(3)
with c1:
    away_next = st.number_input(text.T("forecast_away", lang), 0, 30, 0)
with c2:
    guests_next = st.number_input(text.T("forecast_guests", lang), 0, 20, 0)
with c3:
    summer_next = st.checkbox(text.T("forecast_summer", lang))

st.subheader(text.T("forecast_fuel_sub", lang))
fuel_next = st.number_input(
    text.T("forecast_fuel_label", lang),
    min_value=0.0,
    max_value=10.0,
    value=min(float(last_fuel_rate), 10.0),
    step=0.05,
    help=text.T("forecast_fuel_shock_help", lang),
)

# Baseline projection calculations (capped at 30 days and clamped to AWAY_SHARE * 30 minimum)
away_clamped = min(30.0, max(0.0, float(away_next)))
eff_days = max(AWAY_SHARE * 30.0, (30.0 - away_clamped) + (AWAY_SHARE * away_clamped))
projected_units = (normal_daily * eff_days * (1.15 if summer_next else 1.0)) + (guests_next * 1.2 * 7.0)

low_u, mid_u, hi_u = projected_units * 0.9, projected_units, projected_units * 1.1

b_lo = to_pay(low_u, days=30, kw=kw, fuel=fuel_next, free_units=free)
b_mid = to_pay(mid_u, days=30, kw=kw, fuel=fuel_next, free_units=free)
b_hi = to_pay(hi_u, days=30, kw=kw, fuel=fuel_next, free_units=free)

last_bill_paid = to_pay(float(latest["units"]), days=last_days, kw=kw, fuel=last_fuel_rate, free_units=free)

# 2. Headline in RUPEES
with st.container(border=True):
    st.markdown(f"### {text.T('forecast_est_bill', lang)} {ui_common.rupees(b_lo)} – {ui_common.rupees(b_hi)} (estimate)")
    st.caption(
        f"{text.T('forecast_likely', lang)}: **{ui_common.rupees(b_mid)} (estimate)** (~{mid_u:.0f} units (estimate))"
    )

    # When projected bill is zero under Gruha Jyothi, do not show contradictory breakdown
    if b_mid <= 0:
        st.success(text.T("forecast_zero_bill_gj", lang))
    else:
        # "Rates vs you" line: breaking down change vs last bill, reconciled with headline
        total_diff_rs = round(b_mid - last_bill_paid)
        cost_old_usage_new_rates = to_pay(float(latest["units"]), days=last_days, kw=kw, fuel=fuel_next, free_units=free)
        rate_diff_rs = round(cost_old_usage_new_rates - last_bill_paid)
        usage_diff_rs = total_diff_rs - rate_diff_rs

        if total_diff_rs > 5:
            st.info(
                text.T(
                    "forecast_rates_breakdown_more",
                    lang,
                    diff_rs=abs(total_diff_rs),
                    rate_diff_rs=rate_diff_rs,
                    usage_diff_rs=usage_diff_rs,
                )
            )
        elif total_diff_rs < -5:
            st.info(
                text.T(
                    "forecast_rates_breakdown_less",
                    lang,
                    diff_rs=abs(total_diff_rs),
                    rate_diff_rs=rate_diff_rs,
                    usage_diff_rs=usage_diff_rs,
                )
            )
        else:
            st.info(text.T("forecast_rates_breakdown_same", lang, diff_rs=abs(total_diff_rs)))

    # Fuel shock callout (when fuel_next is higher than last bill's fuel rate)
    if fuel_next > last_fuel_rate:
        fuel_extra_rs = round(fuel_shock(mid_u, 30, kw, last_fuel_rate, fuel_next, free))
        st.warning(text.T("forecast_fuel_shock_callout", lang, extra_rs=fuel_extra_rs))

    # Gruha Jyothi risk warning
    if free is not None and hi_u > GJ_CAP:
        st.error(text.T("forecast_risk_high", lang))

st.markdown("<br>", unsafe_allow_html=True)

# 3. Mid-Month Check (with dynamic billing cycle days)
with st.container(border=True):
    st.subheader(text.T("forecast_mid_sub", lang))
    st.write(text.T("forecast_mid_desc", lang))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        cur_meter = st.number_input(
            text.T("forecast_units_used", lang),
            min_value=0,
            max_value=5000,
            value=min(int(normal_daily * 15), 5000),
        )
    with col_b:
        cur_days = st.number_input(
            text.T("forecast_days_passed", lang),
            min_value=1,
            max_value=35,
            value=15,
        )
    with col_c:
        cycle_days = st.number_input(
            text.T("forecast_cycle_days", lang),
            min_value=25,
            max_value=35,
            value=30,
            help=text.T("forecast_cycle_help", lang),
        )

    days_elapsed = min(cur_days, cycle_days)
    projected_month = (cur_meter / max(days_elapsed, 1)) * cycle_days
    st.markdown(
        f"**{text.T('forecast_paced_usage', lang)}** `{projected_month:.0f} units (estimate)` (for {cycle_days}-day cycle)"
    )

    if free is not None:
        if projected_month > GJ_CAP:
            st.error(text.T("forecast_lose_gj", lang))
        elif projected_month > free:
            st.warning(text.T("forecast_pay_extra", lang, free=round(free), units=round(projected_month - free)))
        else:
            st.success(text.T("forecast_on_track", lang))
