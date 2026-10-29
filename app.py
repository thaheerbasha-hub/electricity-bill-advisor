"""
app.py · Main Entrypoint for Power Bill Coach (Karnataka)
Lead / Frame: THAHEER

Features:
  - Gatekeeper with st.navigation:
      • If not logged in -> Only show Login page (navigation hidden)
      • If logged in -> Full menu (Home, My Bills, What Changed, Results, Forecast, About Karnataka)
  - Full dynamic translation of sidebar navigation based on st.session_state["lang"]
"""

import streamlit as st
import text

st.set_page_config(
    page_title="Power Bill Coach · Karnataka",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State defaults
if "user" not in st.session_state:
    st.session_state["user"] = None

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

lang = st.session_state.get("lang", "en")

# Define pages for st.navigation with bilingual labels
login_page = st.Page("pages/1_Login.py", title=text.T("nav_login", lang), icon="🔐")
home_page = st.Page("pages/2_Home.py", title=text.T("nav_home", lang), icon="⚡", default=True)
bills_page = st.Page("pages/3_My_Bills.py", title=text.T("nav_bills", lang), icon="📄")
what_changed_page = st.Page("pages/4_What_Changed.py", title=text.T("nav_changed", lang), icon="🔍")
results_page = st.Page("pages/5_Results.py", title=text.T("nav_results", lang), icon="📊")
forecast_page = st.Page("pages/6_Forecast.py", title=text.T("nav_forecast", lang), icon="🔮")
about_page = st.Page("pages/7_About_Karnataka.py", title=text.T("nav_about", lang), icon="🏛️")

# Gatekeeper routing:
if not st.session_state.get("user"):
    # When logged out, lock navigation strictly to Login page
    pg = st.navigation([login_page], position="hidden")
else:
    # When logged in, present structured multi-page navigation localized in selected language
    sec_dash = text.T("sec_dashboard", lang)
    sec_analysis = text.T("sec_analysis", lang)
    sec_ref = text.T("sec_reference", lang)

    pg = st.navigation({
        sec_dash: [home_page],
        sec_analysis: [bills_page, what_changed_page, results_page, forecast_page],
        sec_ref: [about_page]
    })

# Execute active page
pg.run()
