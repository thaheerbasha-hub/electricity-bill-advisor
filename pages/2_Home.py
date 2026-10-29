"""
2_Home.py · Power Bill Coach Dashboard
Shows:
  - Personalized Greeting (Hello, Name!)
  - Last Bill Summary & Consumption
  - Gruha Jyothi Meter (units out of 200 cap)
  - Top Alert Banner (e.g. Subsidy at risk, jump alert)
  - Quick action buttons to the other pages
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

# Quick rate constants for Karnataka
RATE = 5.80
FIXED_PER_KW = 150
TAX = 0.09
GJ_CAP = 200

def calc_to_pay(units, days, kw, fuel, free_units):
    energy = units * RATE
    full = energy + kw * FIXED_PER_KW * (days / 30.0) + units * fuel + (energy * TAX)
    if free_units is None or units > GJ_CAP:
        return full
    if units <= free_units:
        return 0.0
    extra = units - free_units
    return extra * (RATE * (1 + TAX) + fuel)

# Fetch user bills
bills = db.get_bills(user["id"])

# Greeting Header
st.title(f"⚡ {text.T('welcome', lang)}, {user['name']}!")
st.caption(text.T("home_subtitle", lang))

st.markdown("<br>", unsafe_allow_html=True)

if not bills:
    st.info("You don't have any bills recorded yet. Add your first bill to see insights and alerts!" if lang == "en" else "ಇನ್ನೂ ಯಾವುದೇ ಬಿಲ್ ದಾಖಲಾಗಿಲ್ಲ. ವಿವರಗಳನ್ನು ನೋಡಲು ನಿಮ್ಮ ಮೊದಲ ಬಿಲ್ ಸೇರಿಸಿ!")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add My First Bill" if lang == "en" else "➕ ಮೊದಲ ಬಿಲ್ ಸೇರಿಸಿ", type="primary", use_container_width=True):
            st.switch_page("pages/3_My_Bills.py")
    with c2:
        if st.button("⚡ Load Demo Bills" if lang == "en" else "⚡ ಮಾದರಿ ಬಿಲ್‌ಗಳನ್ನು ಲೋಡ್ ಮಾಡಿ", use_container_width=True):
            sample_bills = [
                ("May 2026", 152.0, 30, 0, 0.35, 150.0, 2.0),
                ("Jun 2026", 160.0, 31, 0, 0.35, 150.0, 2.0),
                ("Jul 2026", 148.0, 30, 0, 0.35, 150.0, 2.0),
                ("Aug 2026", 155.0, 31, 0, 0.37, 150.0, 2.0),
                ("Sep 2026", 168.0, 30, 0, 0.37, 150.0, 2.0),
                ("Oct 2026", 206.0, 31, 0, 0.37, 150.0, 2.0),
            ]
            for b in sample_bills:
                db.add_bill(user["id"], b[0], b[1], b[2], b[3], b[4], b[5], b[6])
            st.success("Demo bills loaded!")
            st.rerun()
    st.stop()

# Analyze latest bill vs previous bill
latest = bills[-1]
prev = bills[-2] if len(bills) > 1 else None

latest_pay = calc_to_pay(latest["units"], latest["days"], latest["load_kw"], latest["fuel_rs"], latest["free_units"])
prev_pay = calc_to_pay(prev["units"], prev["days"], prev["load_kw"], prev["fuel_rs"], prev["free_units"]) if prev else None
delta_pay = (latest_pay - prev_pay) if prev_pay is not None else 0

daily_units = latest["units"] / max(latest["days"], 1)

# --- 1. TOP ALERT BANNER ---
if latest["units"] > GJ_CAP and latest.get("free_units"):
    if lang == "kn":
        st.error(
            f"🚨 **ಗೃಹ ಜ್ಯೋತಿ ಮಿತಿ ಮೀರಿದೆ!** ಈ ತಿಂಗಳು ನಿಮ್ಮ ಬಳಕೆ **{latest['units']:.0f} ಯೂನಿಟ್‌ಗಳು** ತಲುಪಿದ್ದು, "
            f"ಸರ್ಕಾರದ 200 ಯೂನಿಟ್ ಮಿತಿಯನ್ನು ಮೀರಿದೆ. ಇದರಿಂದಾಗಿ ಈ ತಿಂಗಳು ₹0 ಸಬ್ಸಿಡಿ ರದ್ದಾಗಿದ್ದು, "
            f"ನೀವು ಪೂರ್ಣ ಬಿಲ್ **{ui_common.rupees(latest_pay)}** ಪಾವತಿಸಬೇಕಾಗುತ್ತದೆ."
        )
    else:
        st.error(
            f"🚨 **Gruha Jyothi Threshold Exceeded!** This month your usage hit **{latest['units']:.0f} units**, "
            f"crossing the 200-unit government cap. As a result, you lose the ₹0 subsidy for this month and "
            f"must pay the full bill of **{ui_common.rupees(latest_pay)}**."
        )
elif latest["units"] > (GJ_CAP - 15) and latest.get("free_units"):
    if lang == "kn":
        st.warning(
            f"⚠️ **ಎಚ್ಚರಿಕೆ: 200 ಯೂನಿಟ್ ಮಿತಿಯ ಸಮೀಪದಲ್ಲಿದ್ದೀರಿ!** ನೀವು **{latest['units']:.0f} ಯೂನಿಟ್‌ಗಳನ್ನು** ಬಳಸಿದ್ದೀರಿ. "
            f"ಕೇವಲ {GJ_CAP - latest['units']:.0f} ಯೂನಿಟ್‌ಗಳು ಹೆಚ್ಚಾದರೆ ಉಚಿತ ವಿದ್ಯುತ್ ರದ್ದಾಗುತ್ತದೆ!"
        )
    else:
        st.warning(
            f"⚠️ **Caution: Close to 200 units cap!** You consumed **{latest['units']:.0f} units** this month. "
            f"Just {GJ_CAP - latest['units']:.0f} more units would have triggered a full bill instead of free electricity!"
        )
elif delta_pay > 500:
    st.warning(
        f"📈 **Bill Jump Detected / ಬಿಲ್ ಹೆಚ್ಚಳ:** Your bill rose by **{ui_common.rupees(delta_pay)}** compared to last month."
    )
else:
    st.success("✅ **ಬಳಕೆ ಸಾಮಾನ್ಯ ಮಿತಿಯಲ್ಲಿದೆ / Consumption Normal:** Your usage is steady and under control this month.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 2. SUMMARY METRIC CARDS ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(
        label=text.T("metric_latest_bill", lang),
        value=ui_common.rupees(latest_pay),
        delta=f"{'+' if delta_pay > 0 else ''}{ui_common.rupees(delta_pay)}" if prev else None,
        delta_color="inverse"
    )
with m2:
    st.metric(
        label=text.T("metric_units", lang),
        value=f"{latest['units']:.0f} u",
        delta=f"{latest['units'] - prev['units']:+.0f} u" if prev else None,
        delta_color="inverse"
    )
with m3:
    st.metric(
        label=text.T("metric_daily", lang),
        value=f"{daily_units:.1f} u/d",
        help="Units per day"
    )
with m4:
    if not latest.get("free_units"):
        gj_status = text.T("gj_not_enrolled", lang)
    elif latest["units"] > GJ_CAP:
        gj_status = text.T("gj_lost", lang)
    elif latest["units"] <= (latest["free_units"] or 0):
        gj_status = text.T("gj_free", lang)
    else:
        gj_status = text.T("gj_partial", lang)

    st.metric(
        label=text.T("metric_gj_status", lang),
        value=gj_status
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- 3. GRUHA JYOTHI METER ---
with st.container(border=True):
    st.subheader(text.T("meter_title", lang))
    st.caption(text.T("meter_caption", lang))
    
    pct = min(latest["units"] / GJ_CAP, 1.0)
    st.progress(pct)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(
            f"**{latest['units']:.0f} / {GJ_CAP} Units** ({(latest['units']/GJ_CAP)*100:.0f}%)"
        )
        if latest["units"] <= GJ_CAP:
            st.markdown(f"🟢 **{text.T('units_buffer', lang)}** `{GJ_CAP - latest['units']:.0f} units`")
        else:
            st.markdown(f"🔴 **{text.T('units_over', lang)}** `{latest['units'] - GJ_CAP:.0f} units`")
    with col_b:
        st.caption(f"**{latest['month']}** ({latest['days']} days)")

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. ACTION BUTTONS ---
st.subheader(text.T("quick_nav", lang))

c1, c2, c3, c4 = st.columns(4)

with c1:
    with st.container(border=True):
        st.markdown(f"#### {text.T('nav_bills', lang)}")
        st.caption(text.T("nav_bills_desc", lang))
        if st.button("Open →" if lang == "en" else "ತೆರೆಯಿರಿ →", key="btn_nav_bills", use_container_width=True):
            st.switch_page("pages/3_My_Bills.py")

with c2:
    with st.container(border=True):
        st.markdown(f"#### {text.T('nav_changed', lang)}")
        st.caption(text.T("nav_changed_desc", lang))
        if st.button("Open →" if lang == "en" else "ತೆರೆಯಿರಿ →", key="btn_nav_changed", use_container_width=True):
            st.switch_page("pages/4_What_Changed.py")

with c3:
    with st.container(border=True):
        st.markdown(f"#### {text.T('nav_results', lang)}")
        st.caption(text.T("nav_results_desc", lang))
        if st.button("Open →" if lang == "en" else "ತೆರೆಯಿರಿ →", key="btn_nav_results", use_container_width=True):
            st.switch_page("pages/5_Results.py")

with c4:
    with st.container(border=True):
        st.markdown(f"#### {text.T('nav_forecast', lang)}")
        st.caption(text.T("nav_forecast_desc", lang))
        if st.button("Open →" if lang == "en" else "ತೆರೆಯಿರಿ →", key="btn_nav_forecast", use_container_width=True):
            st.switch_page("pages/6_Forecast.py")
