"""
2_Home.py · Power Bill Coach Dashboard
Shows:
  - Personalized Greeting (Hello, Name!)
  - Last Bill Summary & Consumption
  - Gruha Jyothi Meter (units out of 200 cap)
  - Top Alert Banner (e.g. Subsidy at risk, jump alert)
  - Quick action buttons to the other pages
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
if lang == "kn":
    st.title(f"⚡ ನಮಸ್ಕಾರ, {user['name']}!")
    st.caption("ನಿಮ್ಮ ಮನೆಯ ಬೆಸ್ಕಾಂ ವಿದ್ಯುತ್ ಖಾತೆಯ ಇತ್ತೀಚಿನ ವಿವರಗಳು")
else:
    st.title(f"⚡ Welcome back, {user['name']}!")
    st.caption("Here is your household's latest BESCOM electricity overview")

st.markdown("<br>", unsafe_allow_html=True)

if not bills:
    st.info("You don't have any bills recorded yet. Add your first bill to see insights and alerts!")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add My First Bill", type="primary", use_container_width=True):
            st.switch_page("pages/3_My_Bills.py")
    with c2:
        if st.button("⚡ Load Demo Bills", use_container_width=True):
            # Load sample bills for this user
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
    st.error(
        f"🚨 **Gruha Jyothi Threshold Exceeded!** This month your usage hit **{latest['units']:.0f} units**, "
        f"crossing the 200-unit government cap. As a result, you lose the ₹0 subsidy for this month and "
        f"must pay the full bill of **{ui_common.rupees(latest_pay)}**."
    )
elif latest["units"] > (GJ_CAP - 15) and latest.get("free_units"):
    st.warning(
        f"⚠️ **Caution: Close to 200 units cap!** You consumed **{latest['units']:.0f} units** this month. "
        f"Just {GJ_CAP - latest['units']:.0f} more units would have triggered a full bill instead of free electricity!"
    )
elif delta_pay > 500:
    st.warning(
        f"📈 **Bill Jump Detected:** Your bill rose by **{ui_common.rupees(delta_pay)}** compared to last month. "
        f"Check the **What Changed** tab to see what caused this increase."
    )
else:
    st.success("✅ **Consumption in Normal Range:** Your usage is steady and under control this month.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 2. SUMMARY METRIC CARDS ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(
        label="Latest Bill to Pay" if lang == "en" else "ಈ ತಿಂಗಳ ಬಿಲ್",
        value=ui_common.rupees(latest_pay),
        delta=f"{'+' if delta_pay > 0 else ''}{ui_common.rupees(delta_pay)} vs prev" if prev else None,
        delta_color="inverse"
    )
with m2:
    st.metric(
        label="Units Consumed" if lang == "en" else "ಬಳಸಿದ ಯೂನಿಟ್‌ಗಳು",
        value=f"{latest['units']:.0f} units",
        delta=f"{latest['units'] - prev['units']:+.0f} units" if prev else None,
        delta_color="inverse"
    )
with m3:
    st.metric(
        label="Daily Average" if lang == "en" else "ದೈನಂದಿನ ಸರಾಸರಿ",
        value=f"{daily_units:.1f} u/day",
        help="Calculated as total units divided by billing days"
    )
with m4:
    gj_status = "Not Enrolled" if not latest.get("free_units") else (
        "Lost (200+ units)" if latest["units"] > GJ_CAP else (
            "₹0 (Full Free)" if latest["units"] <= (latest["free_units"] or 0) else "Partly Free"
        )
    )
    st.metric(
        label="Gruha Jyothi Scheme" if lang == "en" else "ಗೃಹ ಜ್ಯೋತಿ ಸ್ಥಿತಿ",
        value=gj_status
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- 3. GRUHA JYOTHI METER (Units out of 200 cap) ---
with st.container(border=True):
    st.subheader("🎯 Gruha Jyothi 200-Unit Safety Meter")
    st.caption("In Karnataka, keeping your monthly usage under 200 units keeps your subsidized rate active.")
    
    pct = min(latest["units"] / GJ_CAP, 1.0)
    bar_color = "#10b981" if latest["units"] <= 175 else ("#f59e0b" if latest["units"] <= GJ_CAP else "#ef4444")
    
    st.progress(pct)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(
            f"**Current: {latest['units']:.0f} / {GJ_CAP} Units** "
            f"({(latest['units']/GJ_CAP)*100:.0f}% of cap)"
        )
        if latest["units"] <= GJ_CAP:
            st.markdown(f"🟢 **Buffer left:** `{GJ_CAP - latest['units']:.0f} units` before losing the ₹0 scheme.")
        else:
            st.markdown(f"🔴 **Over the line by:** `{latest['units'] - GJ_CAP:.0f} units` — scheme invalid this cycle.")
    with col_b:
        st.caption(f"Billing period: **{latest['month']}** ({latest['days']} days)")

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. ACTION BUTTONS TO OTHER PAGES ---
st.subheader("⚡ Quick Navigation")
st.write("Explore your bill analytics, diagnose waste, and plan next month:")

c1, c2, c3, c4 = st.columns(4)

with c1:
    with st.container(border=True):
        st.markdown("#### 📄 My Bills")
        st.caption("View bill history, add new monthly bills, or manage records.")
        if st.button("Open Bills →", key="btn_nav_bills", use_container_width=True):
            st.switch_page("pages/3_My_Bills.py")

with c2:
    with st.container(border=True):
        st.markdown("#### 🔍 What Changed")
        st.caption("Answer simple questions about guests, vacations, heat, or motors.")
        if st.button("Diagnose Jump →", key="btn_nav_changed", use_container_width=True):
            st.switch_page("pages/4_What_Changed.py")

with c3:
    with st.container(border=True):
        st.markdown("#### 📊 Results & Waste")
        st.caption("See waterfall breakdown, vacation tests, and tailored saving tips.")
        if st.button("View Insights →", key="btn_nav_results", use_container_width=True):
            st.switch_page("pages/5_Results.py")

with c4:
    with st.container(border=True):
        st.markdown("#### 🔮 Next Forecast")
        st.caption("Project next month's bill, simulate fuel shocks, and mid-month test.")
        if st.button("See Forecast →", key="btn_nav_forecast", use_container_width=True):
            st.switch_page("pages/6_Forecast.py")
