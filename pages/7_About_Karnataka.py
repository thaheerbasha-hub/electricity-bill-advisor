"""
7_About_Karnataka.py · Karnataka Electricity Context & BESCOM Data
Assigned to: AKSHAR
Features:
  - BESCOM consumer breakdown
  - Gruha Jyothi rules & tariff structure
  - How Power Bill Coach works behind the scenes
  - Fully bilingual (English / Kannada)
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import ui_common
import text

ui_common.apply_custom_css()
ui_common.render_sidebar()

lang = st.session_state.get("lang", "en")

st.title(text.T("about_title", lang))
st.caption(text.T("about_caption", lang))

st.subheader(text.T("about_tariff_sub", lang))
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    col1.metric(text.T("about_flat_energy", lang), "₹5.80 / unit")
    col2.metric(text.T("about_fixed_charge", lang), "₹150 / kW / month")
    col3.metric(text.T("about_tax", lang), "9%")
    st.caption("FPPCA (Fuel adjustment charge) is revised quarterly based on generation costs." if lang == "en" else "FPPCA (ಇಂಧನ ಹೊಂದಾಣಿಕೆ ಶುಲ್ಕ) ಅನ್ನು ಉತ್ಪಾದನಾ ವೆಚ್ಚದ ಆಧಾರದ ಮೇಲೆ ತ್ರೈಮಾಸಿಕವಾಗಿ ಪರಿಷ್ಕರಿಸಲಾಗುತ್ತದೆ.")

st.subheader(text.T("about_gj_sub", lang))
with st.container(border=True):
    if lang == "kn":
        st.markdown("""
        - **ಸಬ್ಸಿಡಿ ನಿಯಮ:** ಅರ್ಹ ಗ್ರಾಹಕರು ತಮ್ಮ 12 ತಿಂಗಳ ಸರಾಸರಿ ಬಳಕೆಯ ಆಧಾರದಲ್ಲಿ (10% ಬಫರ್ ಸೇರಿ) ಉಚಿತ ವಿದ್ಯುತ್ ಪಡೆಯುತ್ತಾರೆ.
        - **200 ಯೂನಿಟ್ ಮಿತಿ:** ಯಾವುದೇ ತಿಂಗಳಲ್ಲಿ ನಿಮ್ಮ ಒಟ್ಟು ಬಳಕೆ **200 ಯೂನಿಟ್** ಮೀರಿದರೆ, ಆ ತಿಂಗಳ ಪೂರ್ಣ ಸಬ್ಸಿಡಿ ರದ್ದಾಗುತ್ತದೆ ಮತ್ತು ಪೂರ್ಣ ಬಿಲ್ ಪಾವತಿಸಬೇಕಾಗುತ್ತದೆ.
        - **ಭಾಗಶಃ ಬಿಲ್ಲಿಂಗ್:** ಬಳಕೆ ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಕೋಟಾಕ್ಕಿಂತ ಹೆಚ್ಚಿದ್ದು, ಆದರೆ 200 ಯೂನಿಟ್‌ಗಳ ಒಳಗೆ ಇದ್ದರೆ, ಕೇವಲ ಹೆಚ್ಚುವರಿ ಯೂನಿಟ್‌ಗಳಿಗೆ ಮಾತ್ರ ಶುಲ್ಕ ವಿಧಿಸಲಾಗುತ್ತದೆ.
        """)
    else:
        st.markdown("""
        - **Subsidy Basis:** Eligible consumers receive free electricity up to their 12-month average entitlement (+10% buffer).
        - **The 200-Unit Cliff:** If total monthly consumption crosses **200 units**, the subsidy is entirely forfeited for that month, and the consumer pays the full bill.
        - **Partial Billing:** If consumption is above your individual quota but under 200 units, you only pay for the extra units.
        """)

st.subheader(text.T("about_escoms_sub", lang))
df_escoms = pd.DataFrame({
    "ESCOM": ["BESCOM (Bengaluru)", "HESCOM (Hubballi)", "GESCOM (Kalaburagi)", "MESCOM (Mangaluru)", "CESC (Mysuru)"],
    "Domestic Consumers (Millions)": [10.2, 4.8, 3.2, 2.5, 3.4]
})
fig = px.bar(df_escoms, x="ESCOM", y="Domestic Consumers (Millions)", color="ESCOM")
fig.update_layout(showlegend=False, height=350)
st.plotly_chart(fig, use_container_width=True)
