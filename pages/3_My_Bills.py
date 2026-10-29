"""
3_My_Bills.py · Manage Monthly Electricity Bills
Assigned to: ARNAV
Features:
  - Add bill form (Month, Units, Days, Estimated?, Fuel surcharge ₹, Free units, Sanctioned load kW)
  - Interactive table of past bills
  - Delete / Edit options
  - Fully bilingual (English / Kannada)
"""

import streamlit as st
import pandas as pd
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

st.title(text.T("bills_title", lang))
st.caption(text.T("bills_caption", lang))

bills = db.get_bills(user["id"])

# --- Add Bill Section ---
with st.expander(text.T("bills_add_expander", lang), expanded=len(bills) == 0):
    with st.form("add_bill_form"):
        c1, c2 = st.columns(2)
        with c1:
            month = st.text_input(text.T("bill_month_label", lang), placeholder="e.g. Nov 2026")
            units = st.number_input(text.T("bill_units_label", lang), min_value=0.0, max_value=5000.0, value=170.0, step=1.0)
            days = st.number_input(text.T("bill_days_label", lang), min_value=15, max_value=60, value=30, step=1)
            estimated = st.checkbox(text.T("bill_est_label", lang))
        with c2:
            load_kw = st.number_input(text.T("bill_kw_label", lang), min_value=0.5, max_value=25.0, value=2.0, step=0.5)
            in_gj = st.checkbox(text.T("bill_gj_enrolled", lang), value=True)
            free_units = st.number_input(text.T("bill_free_label", lang), min_value=0, max_value=200, value=150, step=1) if in_gj else None
            fuel_rs = st.number_input(text.T("bill_fuel_label", lang), min_value=0.0, max_value=5.0, value=0.37, step=0.01)

        submitted = st.form_submit_button(text.T("bill_save_btn", lang), type="primary", use_container_width=True)
        if submitted:
            if not month.strip():
                st.error("Please enter a month label." if lang == "en" else "ದಯವಿಟ್ಟು ತಿಂಗಳ ಹೆಸರು ನಮೂದಿಸಿ.")
            else:
                db.add_bill(user["id"], month, units, days, estimated, fuel_rs, free_units, load_kw)
                st.success("Bill record saved successfully!" if lang == "en" else "ಬಿಲ್ ದಾಖಲೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ!")
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- Bills Table ---
if bills:
    st.subheader(f"{text.T('bills_saved_sub', lang)} ({len(bills)})")
    table_data = []
    for b in bills:
        table_data.append({
            "ID": b["id"],
            "Month" if lang == "en" else "ತಿಂಗಳು": b["month"],
            "Units" if lang == "en" else "ಯೂನಿಟ್": f"{b['units']:.0f}",
            "Days" if lang == "en" else "ದಿನಗಳು": b["days"],
            "Daily Avg" if lang == "en" else "ದೈನಂದಿನ ಸರಾಸರಿ": f"{b['units']/max(b['days'], 1):.1f} u/d",
            "Reading Type" if lang == "en" else "ರೀಡಿಂಗ್ ಮಾದರಿ": ("Estimate ⚠️" if b["estimated"] else "Actual ✅"),
            "Load (kW)": f"{b['load_kw']} kW",
            "Fuel ₹/u": f"₹{b['fuel_rs']:.2f}",
            "Free Units": b["free_units"] if b["free_units"] is not None else "N/A"
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

    # Delete bill option
    with st.expander(text.T("bills_delete_sub", lang)):
        del_id = st.selectbox("Select Bill to Delete" if lang == "en" else "ಅಳಿಸಲು ಬಿಲ್ ಆಯ್ಕೆಮಾಡಿ", options=[b["id"] for b in bills], format_func=lambda i: next(f"ID {b['id']} - {b['month']} ({b['units']} units)" for b in bills if b["id"] == i))
        if st.button(text.T("bills_del_btn", lang), type="secondary"):
            db.delete_bill(del_id, user["id"])
            st.success("Bill deleted." if lang == "en" else "ಬಿಲ್ ಅಳಿಸಲಾಗಿದೆ.")
            st.rerun()
else:
    st.info("No bills saved yet. Fill out the form above to record your first bill!" if lang == "en" else "ಇನ್ನೂ ಯಾವುದೇ ಬಿಲ್‌ಗಳು ದಾಖಲಾಗಿಲ್ಲ. ಮೇಲೆ ನೀಡಿರುವ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಿ!")
