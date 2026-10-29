"""
pages/5_Results.py · Results & Insights Breakdown
Assigned to: RISHABH (HackNova-26, Problem P01)

Features:
  - Card 1 'Why your bill changed': headline rupees up/down, biggest reason, each reason with its rupees and tag, plus a Plotly waterfall from last bill to this bill. All from engine.explain(bills, answers).
  - Card 2 'Where the waste is': waste_checks() results as coloured messages (red / amber / green).
  - Card 3 'How to save': top tips from tips(), each with the rupees-saved range and cost.
  - Fully bilingual (English / Kannada via text.T) and themed with ui_common.
  - Safe against 0 bills or unauthenticated access.
"""

import plotly.graph_objects as go
import streamlit as st

import db
import ui_common
import text
import questions

# Direct import from engine (no TEMP fallback — engine is stable)
from engine import explain, to_pay

# Ensure user dict compatibility for ui_common
if isinstance(st.session_state.get("user"), dict):
    st.session_state["user"].setdefault("name", st.session_state["user"].get("id", "User"))

# Apply global styling and persistent sidebar
ui_common.apply_custom_css()
ui_common.render_sidebar()

lang = st.session_state.get("lang", "en")
user = st.session_state.get("user")

# Header
title_text = text.T("results_title", lang)
if title_text == "results_title":
    title_text = "Electricity Bill Results"
st.title(title_text)

caption_text = text.T("results_caption", lang)
if caption_text == "results_caption":
    caption_text = "“Not every bill jump is your fault. We show you exactly which part is.”"
st.caption(caption_text)

# -----------------------------------------------------------------------------
# User & Session Validation (Must not crash if not logged in or 0 bills)
# -----------------------------------------------------------------------------
user_id = "demo_user"
if not user:
    st.info("👋 " + ("Viewing in guest mode. To save your household history, log in or switch to an account."
                     if lang == "en" else
                     "ಅತಿಥಿಯಾಗಿ ವೀಕ್ಷಿಸುತ್ತಿದ್ದೀರಿ. ಬಿಲ್ ಇತಿಹಾಸವನ್ನು ಉಳಿಸಲು ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ."))
else:
    user_id = user.get("id", "demo_user") if isinstance(user, dict) else str(user)
    user_name = user.get("name", user_id) if isinstance(user, dict) else user_id
    st.caption(f"👤 Account: **{user_name}**")

# Check answers
answers = st.session_state.get("answers") or st.session_state.get("bill_answers")
if not answers:
    st.warning("📋 " + ("No household answers found yet." if lang == "en" else "ಯಾವುದೇ ಪ್ರಶ್ನೆಗಳ ಉತ್ತರಗಳು ದಾಖಲಾಗಿಲ್ಲ."))
    st.caption("Please complete the What Changed? questionnaire to see your personalized bill diagnosis."
               if lang == "en" else
               "ನಿಮ್ಮ ಬಿಲ್ ಬದಲಾವಣೆ ವಿಶ್ಲೇಷಿಸಲು ದಯವಿಟ್ಟು 'ಏನು ಬದಲಾಗಿದೆ?' ಪುಟದಲ್ಲಿ ಉತ್ತರಿಸಿ.")
    c1, _ = st.columns([1, 2])
    with c1:
        try:
            st.page_link("pages/4_What_Changed.py", label="Open What Changed? Questionnaire →" if lang == "en" else "ಏನು ಬದಲಾಗಿದೆ ಪುಟಕ್ಕೆ ಹೋಗಿ →", icon="📝")
        except Exception:
            st.markdown("[👉 **What Changed?**](4_What_Changed)")

    if st.button("Preview with sample answers" if lang == "en" else "ಮಾದರಿ ಉತ್ತರಗಳೊಂದಿಗೆ ವೀಕ್ಷಿಸಿ"):
        st.session_state["answers"] = {
            "vacation_days": 0, "guests_people": 2, "guests_days": 6, "hot_ac": True,
            "geyser": True, "home_more": False, "pump": False, "new_items": ["AC"],
            "festival_lights": False, "power_cuts": False
        }
        st.rerun()
    st.stop()

norm_answers = questions.normalize_answers(answers)

try:
    bills = db.get_bills(user_id)
except Exception:
    bills = st.session_state.get("bills", [])

# Zero Bills Edge Case (Must not crash)
if not bills:
    st.warning("⚠️ " + ("No electricity bills found for this account." if lang == "en" else "ಈ ಖಾತೆಯಲ್ಲಿ ಯಾವುದೇ ಬಿಲ್‌ಗಳು ಕಂಡುಬಂದಿಲ್ಲ."))
    st.caption("Add your bills in My Bills to see your component waterfall breakdown and verified waste checks."
               if lang == "en" else
               "ವಾಟರ್‌ಫಾಲ್ ಚಾರ್ಟ್ ಮತ್ತು ನಷ್ಟ ತಪಾಸಣೆ ನೋಡಲು 'ನನ್ನ ಬಿಲ್‌ಗಳು' ಪುಟದಲ್ಲಿ ಬಿಲ್ ಸೇರಿಸಿ.")
    if st.button("Load sample bills for preview" if lang == "en" else "ಮಾದರಿ ಬಿಲ್‌ಗಳನ್ನು ಲೋಡ್ ಮಾಡಿ"):
        st.session_state["bills"] = [
            {"month": "August", "units": 155.0, "days": 30, "away": 0, "fuel_per_unit": 0.0, "estimated": False, "load_kw": 2.0, "free_units": 150},
            {"month": "September", "units": 245.0, "days": 31, "away": 0, "fuel_per_unit": 0.35, "estimated": False, "load_kw": 2.0, "free_units": 150}
        ]
        st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# Bill Math via engine.explain(bills, answers)
# -----------------------------------------------------------------------------
cur_bill = bills[-1]
prev_bill = bills[-2] if len(bills) >= 2 else None

try:
    reasons, total_rupees, normal = explain(bills, norm_answers)
except Exception:
    reasons, total_rupees, normal = [], 0.0, 5.0

# Calculate payable amounts
kw_cur = float(cur_bill.get("load_kw", cur_bill.get("kw", 2.0)) or 2.0)
fuel_cur = float(cur_bill.get("fuel_per_unit", cur_bill.get("fuel", 0.0)) or 0.0)
free_cur = cur_bill.get("free_units", cur_bill.get("free"))
pay_cur = to_pay(float(cur_bill.get("units", 0.0)), int(cur_bill.get("days", 30)), kw_cur, fuel_cur, free_cur)

if prev_bill:
    kw_prev = float(prev_bill.get("load_kw", prev_bill.get("kw", 2.0)) or 2.0)
    fuel_prev = float(prev_bill.get("fuel_per_unit", prev_bill.get("fuel", 0.0)) or 0.0)
    free_prev = prev_bill.get("free_units", prev_bill.get("free"))
    pay_prev = to_pay(float(prev_bill.get("units", 0.0)), int(prev_bill.get("days", 30)), kw_prev, fuel_prev, free_prev)
else:
    pay_prev = 0.0

st.divider()

# Quick summary row
qm1, qm2, qm3 = st.columns(3)
qm1.metric("Current Bill" if lang == "en" else "ಪ್ರಸ್ತುತ ಬಿಲ್", ui_common.rupees(pay_cur))
if prev_bill:
    qm2.metric("Previous Bill" if lang == "en" else "ಹಿಂದಿನ ಬಿಲ್", ui_common.rupees(pay_prev))
    qm3.metric(
        "Net Rupee Change" if lang == "en" else "ಒಟ್ಟು ವ್ಯತ್ಯಾಸ",
        f"{'+' if total_rupees > 0 else ''}{ui_common.rupees(total_rupees)}",
        delta=ui_common.rupees(total_rupees),
        delta_color="inverse"
    )
else:
    qm2.metric("Units Consumed" if lang == "en" else "ಬಳಸಿದ ಯೂನಿಟ್‌ಗಳು", f"{cur_bill.get('units', 0.0):.0f} units")
    qm3.metric("Normal Pace" if lang == "en" else "ದೈನಂದಿನ ಬಳಕೆ", f"{normal:.1f} units/day")

# -----------------------------------------------------------------------------
# CARD 1: Why your bill changed (RUPEES FIRST)
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.subheader("1 · " + ("Why your bill changed" if lang == "en" else "ನಿಮ್ಮ ಬಿಲ್ ಏಕೆ ಬದಲಾಗಿದೆ?"))

    if not prev_bill:
        st.info("ℹ️ " + ("Only one bill recorded. A second consecutive bill is needed to calculate a month-over-month rupee change and waterfall chart."
                         if lang == "en" else
                         "ಕೇವಲ ಒಂದು ಬಿಲ್ ದಾಖಲಾಗಿದೆ. ವ್ಯತ್ಯಾಸ ಮತ್ತು ವಾಟರ್‌ಫಾಲ್ ಚಾರ್ಟ್ ನೋಡಲು ಕನಿಷ್ಠ 2 ಬಿಲ್‌ಗಳು ಬೇಕು."))
    else:
        # RUPEES FIRST Headline
        if abs(total_rupees) < 20.0:
            st.markdown("### Your bill is about the same as last month. <span style='font-size:0.55em;color:#6b7280;border:1px solid #d1d5db;border-radius:4px;padding:2px 6px;'>(estimate)</span>", unsafe_allow_html=True)
        elif total_rupees > 0:
            st.markdown(f"### Bill went **UP by {ui_common.rupees(total_rupees)}** <span style='font-size:0.55em;color:#6b7280;border:1px solid #d1d5db;border-radius:4px;padding:2px 6px;'>(estimate)</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"### Bill went **DOWN by {ui_common.rupees(abs(total_rupees))}** <span style='font-size:0.55em;color:#6b7280;border:1px solid #d1d5db;border-radius:4px;padding:2px 6px;'>(estimate)</span>", unsafe_allow_html=True)

        # Biggest reason
        if reasons:
            big_r = reasons[0]
            st.markdown(f"**Biggest factor:** `{big_r['key'].replace('_', ' ').capitalize()}` ({'+' if big_r['rupees'] > 0 else ''}{ui_common.rupees(big_r['rupees'])})")

        left_col, right_col = st.columns([1.1, 1], gap="medium")

        with left_col:
            st.markdown("**Rupee Impact Breakdown:**")
            for r in reasons:
                rs = r.get("rupees", 0.0)
                tag = r.get("tag", "your usage")
                colr = "#ef4444" if rs > 0 else "#10b981"
                st.markdown(
                    f"<div style='border-left: 4px solid {colr}; padding: 6px 12px; margin: 8px 0; background-color: rgba(128,128,128,0.06); border-radius: 0 4px 4px 0;'>"
                    f"<b>{r['key'].replace('_', ' ').capitalize()}: {'+' if rs > 0 else ''}{ui_common.rupees(rs)}</b> "
                    f"<span style='color: #6b7280; font-size: 0.85em'>({tag})</span> "
                    f"<span style='font-size: 0.72em; color: #6b7280; border: 1px solid #d1d5db; border-radius: 3px; padding: 1px 4px;'>(estimate)</span><br>"
                    f"<span style='font-size: 0.95em;'>{r.get('text', '')}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        with right_col:
            # Plotly Waterfall from last bill to this bill
            if reasons and len(reasons) > 0:
                waterfall_x = ["Last bill" if lang == "en" else "ಹಿಂದಿನ ಬಿಲ್"] + [r["key"].replace("_", " ").capitalize() for r in reasons] + ["This bill" if lang == "en" else "ಈ ತಿಂಗಳ ಬಿಲ್"]
                waterfall_measure = ["absolute"] + ["relative"] * len(reasons) + ["total"]
                waterfall_y = [pay_prev] + [r["rupees"] for r in reasons] + [0]
                waterfall_text = (
                    [ui_common.rupees(pay_prev)]
                    + [('+' if r['rupees'] > 0 else '') + ui_common.rupees(r['rupees']) for r in reasons]
                    + [ui_common.rupees(pay_cur)]
                )

                fig = go.Figure(go.Waterfall(
                    x=waterfall_x,
                    measure=waterfall_measure,
                    y=waterfall_y,
                    text=waterfall_text,
                    textposition="outside",
                    increasing={"marker": {"color": "#ef4444"}},
                    decreasing={"marker": {"color": "#10b981"}},
                    totals={"marker": {"color": "#3b82f6"}}
                ))
                fig.update_layout(
                    title="<b>Waterfall Analysis (₹)</b>" if lang == "en" else "<b>ವಾಟರ್‌ಫಾಲ್ ವಿಶ್ಲೇಷಣೆ (₹)</b>",
                    height=350,
                    margin=dict(l=10, r=10, t=35, b=10),
                    showlegend=False
                )
                try:
                    st.plotly_chart(fig, width="stretch")
                except TypeError:
                    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# CARD 2: Where the waste is (Coloured messages: red / amber / green)
# -----------------------------------------------------------------------------
checks_results = questions.waste_checks(bills, norm_answers, normal)

with st.container(border=True):
    st.subheader("2 · " + ("Where the waste is" if lang == "en" else "ವಿದ್ಯುತ್ ನಷ್ಟ ಎಲ್ಲಿ ಆಗುತ್ತಿದೆ?"))

    for item in checks_results:
        lvl, msg = item[0], item[1]
        if lvl == "red":
            st.error(msg)
        elif lvl == "amber":
            st.warning(msg)
        else:
            st.success(msg)

# -----------------------------------------------------------------------------
# CARD 3: How to save (Top tips from tips(), each with ₹ saved range & cost)
# -----------------------------------------------------------------------------
tip_results = questions.tips(norm_answers, bills)

with st.container(border=True):
    st.subheader("3 · " + ("How to save" if lang == "en" else "ಹೇಗೆ ಉಳಿಸಬಹುದು?"))

    if not tip_results:
        st.info("No immediate waste identified. Maintain your current electricity usage habits!" if lang == "en" else "ಯಾವುದೇ ಅಸಹಜ ನಷ್ಟ ಕಂಡುಬಂದಿಲ್ಲ. ನಿಮ್ಮ ಉತ್ತಮ ಬಳಕೆಯ ಅಭ್ಯಾಸ ಮುಂದುವರಿಸಿ!")
    else:
        for idx, tip in enumerate(tip_results[:5], start=1):
            msg, u_range, rs_range, cost_val, who_val = tip[0], tip[1], tip[2], tip[3], tip[4]

            st.markdown(f"**{idx}. {msg}**")
            b1, b2, b3 = st.columns(3)
            with b1:
                st.markdown(f"💰 **Rupees Saved:** `{rs_range}`" if lang == "en" else f"💰 **ಉಳಿತಾಯ:** `{rs_range}`")
            with b2:
                st.markdown(f"⚡ **Energy Saved:** `{u_range}`" if lang == "en" else f"⚡ **ಯೂನಿಟ್ ಉಳಿತಾಯ:** `{u_range}`")
            with b3:
                st.markdown(f"🛠️ **Cost:** `{cost_val}` · *Target: {who_val}*" if lang == "en" else f"🛠️ **ವೆಚ್ಚ:** `{cost_val}` · *{who_val}*")

            if idx < min(len(tip_results), 5):
                st.divider()

# Footer navigation
st.markdown("<br>", unsafe_allow_html=True)
c_nav, _ = st.columns([1, 1])
with c_nav:
    try:
        st.page_link("pages/4_What_Changed.py", label="← Back to What Changed Questionnaire" if lang == "en" else "← ಏನು ಬದಲಾಗಿದೆ ಪ್ರಶ್ನಾವಳಿಗೆ ಹಿಂತಿರುಗಿ", icon="📝")
    except Exception:
        st.markdown("[← **Back to What Changed Questionnaire**](4_What_Changed)")
