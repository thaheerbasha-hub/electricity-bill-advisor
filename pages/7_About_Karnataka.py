"""
7_About_Karnataka.py · Karnataka Electricity Context & BESCOM Data
Assigned to: AKSHAR
Features:
  - BESCOM consumer breakdown
  - Gruha Jyothi rules & tariff structure
  - How Power Bill Coach works behind the scenes
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import ui_common

ui_common.apply_custom_css()
ui_common.render_sidebar()

st.title("🏛️ About Karnataka Power & BESCOM Tariff Guide")
st.caption("Understanding Karnataka's electricity regulations, the Gruha Jyothi scheme, and tariff calculations.")

st.subheader("1 · Domestic Tariff Structure (BESCOM LT-2)")
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    col1.metric("Flat Energy Charge", "₹5.80 / unit")
    col2.metric("Fixed Charge", "₹150 / kW / month")
    col3.metric("State Electricity Duty", "9% on energy")
    st.caption("Note: Fuel Adjustment Charge (FPPCA) is revised quarterly based on generation costs.")

st.subheader("2 · How the Gruha Jyothi Scheme Works")
with st.container(border=True):
    st.markdown("""
    - **Subsidy Basis:** Eligible consumers receive free electricity up to their 12-month calculated average entitlement (plus 10% buffer), subject to a maximum cap.
    - **The 200-Unit Cliff:** If total monthly consumption crosses **200 units**, the subsidy is entirely forfeited for that month, and the consumer pays the full bill.
    - **Partial Billing:** If consumption is above your individual sanctioned quota but under 200 units, you only pay for the units exceeding your quota.
    """)

st.subheader("3 · Karnataka ESCOMs Overview")
df_escoms = pd.DataFrame({
    "ESCOM": ["BESCOM (Bengaluru)", "HESCOM (Hubballi)", "GESCOM (Kalaburagi)", "MESCOM (Mangaluru)", "CESC (Mysuru)"],
    "Approx Domestic Consumers (Millions)": [10.2, 4.8, 3.2, 2.5, 3.4]
})
fig = px.bar(df_escoms, x="ESCOM", y="Approx Domestic Consumers (Millions)", color="ESCOM",
             title="Domestic Consumer Base Across Karnataka Distribution Companies")
fig.update_layout(showlegend=False, height=350)
st.plotly_chart(fig, use_container_width=True)
