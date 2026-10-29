"""
7_About_Karnataka.py · Karnataka Electricity Context & BESCOM Data
Assigned to: AKSHAR
Features:
  - Real BESCOM public dataset analytics (computed directly from CSVs)
  - Gruha Jyothi rules & tariff structure
  - Future roadmap scope
  - Fully bilingual (English / Kannada)
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path
import ui_common
import text

# Shared imports with safe temporary fallbacks
try:
    from engine import RATE, FIXED_PER_KW, TAX, GJ_CAP
except ImportError:
    # TEMP until engine.py is ready
    RATE = 5.80
    FIXED_PER_KW = 150
    TAX = 0.09
    GJ_CAP = 200

ui_common.apply_custom_css()
ui_common.render_sidebar()

lang = st.session_state.get("lang", "en")

st.title(text.T("about_title", lang))
st.caption(text.T("about_caption", lang))

# 1. Domestic Tariff Structure
st.subheader(text.T("about_tariff_sub", lang))
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    col1.metric(text.T("about_flat_energy", lang), f"Rs {RATE:.2f} / unit")
    col2.metric(text.T("about_fixed_charge", lang), f"Rs {FIXED_PER_KW:.0f} / kW / month")
    tax_pct = int(TAX * 100 if TAX < 1 else TAX)
    col3.metric(text.T("about_tax", lang), f"{tax_pct}%")
    st.caption("FPPCA (Fuel adjustment charge) is revised quarterly based on generation costs." if lang == "en" else "FPPCA (ಇಂಧನ ಹೊಂದಾಣಿಕೆ ಶುಲ್ಕ) ಅನ್ನು ವಿದ್ಯುತ್ ಉತ್ಪಾದನಾ ವೆಚ್ಚದ ಆಧಾರದ ಮೇಲೆ ತ್ರೈಮಾಸಿಕವಾಗಿ ಪರಿಷ್ಕರಿಸಲಾಗುತ್ತದೆ.")

# 2. Gruha Jyothi Scheme Explanation
st.subheader(text.T("about_gj_sub", lang))
with st.container(border=True):
    if lang == "kn":
        st.markdown("""
        - **ಸಬ್ಸಿಡಿ ನಿಯಮ:** ಅರ್ಹ ಗ್ರಾಹಕರಿಗೆ ಅವರ ಹಿಂದಿನ 12 ತಿಂಗಳ ಸರಾಸರಿ ಬಳಕೆಯ ಆಧಾರದಲ್ಲಿ (+10% ಹೆಚ್ಚುವರಿ) ಉಚಿತ ವಿದ್ಯುತ್ ನೀಡಲಾಗುತ್ತದೆ.
        - **200 ಯೂನಿಟ್ ಮಿತಿ:** ಒಂದು ತಿಂಗಳಲ್ಲಿ ಒಟ್ಟು ಬಳಕೆ **200 ಯೂನಿಟ್** ಮೀರಿದರೆ, ಆ ತಿಂಗಳ ಸಂಪೂರ್ಣ ಗೃಹ ಜ್ಯೋತಿ ಸಬ್ಸಿಡಿ ರದ್ದಾಗುತ್ತದೆ ಮತ್ತು ಪೂರ್ಣ ಬಿಲ್ ಪಾವತಿಸಬೇಕು.
        - **ಹೆಚ್ಚುವರಿ ಯೂನಿಟ್‌ಗಳು:** ಬಳಕೆ ನಿಮ್ಮ ನಿಗದಿತ ಉಚಿತ ಕೋಟಾಗಿಂತ ಹೆಚ್ಚಾಗಿದ್ದು 200 ಯೂನಿಟ್‌ಗಿಂತ ಕಡಿಮೆಯಿದ್ದರೆ, ಕೇವಲ ಹೆಚ್ಚುವರಿ ಯೂನಿಟ್‌ಗಳಿಗೆ ಮಾತ್ರ ಹಣ ಪಾವತಿಸಬೇಕು.
        """)
    else:
        st.markdown("""
        - **Subsidy Basis:** Eligible consumers receive free electricity up to their 12-month average entitlement (+10% buffer).
        - **The 200-Unit Cliff:** If total monthly consumption crosses **200 units**, the subsidy is entirely forfeited for that month, and the consumer pays the full bill.
        - **Partial Billing:** If consumption is above your individual quota but under 200 units, you only pay for the extra units.
        """)

# Helper to find data files
def find_data_file(filename: str) -> Path | None:
    candidates = [
        Path(__file__).resolve().parent.parent / "data" / "bescom" / filename,
        Path("data") / "bescom" / filename,
        Path(__file__).resolve().parent.parent.parent / "data" / "bescom" / filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

# 3. Real BESCOM Data Analytics (Computed directly from CSVs, never invented)
st.subheader(text.T("about_data_metrics_title", lang))

annual_path = find_data_file("bescom_annual.csv")
ev_path = find_data_file("bescom_ev.csv")
cat_path = find_data_file("bengaluru_category.csv")

# Compute metric values dynamically
consumers_val, consumers_delta = None, None
ev_val, ev_delta = None, None
share_val, share_delta = None, None

df_annual = None

if annual_path:
    try:
        df_annual = pd.read_csv(annual_path)
        c_first = float(df_annual["Consumers in Lakhs"].iloc[0])
        c_last = float(df_annual["Consumers in Lakhs"].iloc[-1])
        c_growth = round(((c_last - c_first) / c_first) * 100)
        consumers_val = f"{c_last:.1f} Lakh"
        consumers_delta = f"+{c_growth}% ({c_first:.1f}L -> {c_last:.1f}L)"
    except Exception:
        pass
else:
    st.info(text.T("about_data_missing", lang, filename="bescom_annual.csv"))

if ev_path:
    try:
        df_ev = pd.read_csv(ev_path)
        ev_row = df_ev[df_ev["Headers"].astype(str).str.contains("LT EV Charging Stations", case=False, na=False)].iloc[0]
        st_20 = int(float(ev_row["2020-21"]))
        st_22 = int(float(ev_row["2022-23"]))
        ev_val = f"{st_22} Stations"
        ev_delta = f"From {st_20} in 2020-21"
    except Exception:
        pass
else:
    st.info(text.T("about_data_missing", lang, filename="bescom_ev.csv"))

if cat_path:
    try:
        df_cat = pd.read_csv(cat_path)
        row_cat = df_cat.iloc[0]
        dom = float(row_cat["Domestic purpose"])
        tot = float(row_cat["Total Consumption"])
        share_pct = round((dom / tot) * 100, 1)
        share_val = f"{share_pct}%"
        share_delta = text.T("about_metric_share_desc", lang)
    except Exception:
        pass
else:
    st.info(text.T("about_data_missing", lang, filename="bengaluru_category.csv"))

# Display computed 3 metric cards if data loaded
if consumers_val and ev_val and share_val:
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric(text.T("about_metric_consumers", lang), consumers_val, delta=consumers_delta)
        m2.metric(text.T("about_metric_ev", lang), ev_val, delta=ev_delta)
        m3.metric(text.T("about_metric_share", lang), share_val, delta=share_delta)

# Display chart of Consumers in Lakhs over time from real data
if df_annual is not None and "Consumers in Lakhs" in df_annual.columns:
    fig = px.bar(
        df_annual,
        x="Year",
        y="Consumers in Lakhs",
        title=text.T("about_chart_title", lang),
        text="Consumers in Lakhs",
        color_discrete_sequence=["#2b5c8f"]
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis_title="Consumers (Lakhs)",
        xaxis_title="Financial Year"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(text.T("about_source_note", lang))

# 4. "Where This Is Going" Future Roadmap Box
st.subheader(f"🚀 {text.T('about_future_title', lang)}")
with st.container(border=True):
    st.markdown(f"""
- 📸 **{text.T('about_future_p1', lang)}**
- 🏘️ **{text.T('about_future_p2', lang)}**
- ☀️ **{text.T('about_future_p3', lang)}**
""")
