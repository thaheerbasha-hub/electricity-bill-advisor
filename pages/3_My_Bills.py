"""
3_My_Bills.py · Manage Monthly Electricity Bills
Assigned to: ARNAV
Features:
  - Add bill form (Month, Units, Days, Estimated?, Fuel surcharge ₹, Free units, Sanctioned load kW)
  - Interactive table of past bills
  - Delete / Edit options
"""

import streamlit as st
import pandas as pd
import db
import ui_common

ui_common.apply_custom_css()
ui_common.render_sidebar()

user = st.session_state.get("user")
if not user:
    st.warning("Please log in first.")
    st.stop()

st.title("📄 My Bills · Electricity History")
st.caption("Keep track of your monthly BESCOM units and charges. At least two bills are needed to explain jumps.")

bills = db.get_bills(user["id"])

# --- Add Bill Section ---
with st.expander("➕ Add a New Monthly Bill", expanded=len(bills) == 0):
    with st.form("add_bill_form"):
        c1, c2 = st.columns(2)
        with c1:
            month = st.text_input("Billing Month / Label", placeholder="e.g. Nov 2026")
            units = st.number_input("Units Consumed (kWh)", min_value=0.0, max_value=5000.0, value=170.0, step=1.0)
            days = st.number_input("Billing Days in Cycle", min_value=15, max_value=60, value=30, step=1)
            estimated = st.checkbox("Estimated Reading? (Door lock / meter not read)")
        with c2:
            load_kw = st.number_input("Sanctioned Load (kW)", min_value=0.5, max_value=25.0, value=2.0, step=0.5)
            in_gj = st.checkbox("Enrolled in Gruha Jyothi", value=True)
            free_units = st.number_input("Free Units Printed on Bill", min_value=0, max_value=200, value=150, step=1) if in_gj else None
            fuel_rs = st.number_input("Fuel Surcharge / FPPCA (₹/unit)", min_value=0.0, max_value=5.0, value=0.37, step=0.01)

        submitted = st.form_submit_button("Save Bill Record", type="primary", use_container_width=True)
        if submitted:
            if not month.strip():
                st.error("Please enter a month label.")
            else:
                db.add_bill(user["id"], month, units, days, estimated, fuel_rs, free_units, load_kw)
                st.success(f"Added bill for {month} successfully!")
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- Bills Table ---
if bills:
    st.subheader(f"Saved Bills ({len(bills)})")
    
    # Display summary cards or table
    table_data = []
    for b in bills:
        table_data.append({
            "ID": b["id"],
            "Month": b["month"],
            "Units": f"{b['units']:.0f}",
            "Days": b["days"],
            "Daily Avg": f"{b['units']/max(b['days'], 1):.1f} u/d",
            "Reading Type": "Estimate ⚠️" if b["estimated"] else "Actual ✅",
            "Load (kW)": f"{b['load_kw']} kW",
            "Fuel ₹/u": f"₹{b['fuel_rs']:.2f}",
            "Free Units": b["free_units"] if b["free_units"] is not None else "N/A"
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

    # Delete bill option
    with st.expander("🗑️ Delete a Bill"):
        del_id = st.selectbox("Select Bill to Delete", options=[b["id"] for b in bills], format_func=lambda i: next(f"ID {b['id']} - {b['month']} ({b['units']} units)" for b in bills if b["id"] == i))
        if st.button("Confirm Delete", type="secondary"):
            db.delete_bill(del_id, user["id"])
            st.success("Bill deleted.")
            st.rerun()
else:
    st.info("No bills saved yet. Fill out the form above to record your first bill!")
