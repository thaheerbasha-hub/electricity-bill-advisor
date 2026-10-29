"""
app.py · Main Entrypoint for Power Bill Coach (Karnataka)
Lead / Frame: THAHEER

Features:
  - Gatekeeper with st.navigation:
      • If not logged in -> Only show Login page (navigation hidden)
      • If logged in -> Full menu (Home, My Bills, What Changed, Results, Forecast, About Karnataka)
  - Manages global state (st.session_state["user"], st.session_state["lang"])
"""

import streamlit as st

# Configure wide layout, brand title and icon
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

# Define pages for st.navigation
login_page = st.Page("pages/1_Login.py", title="Login / Sign Up", icon="🔐")
home_page = st.Page("pages/2_Home.py", title="Home Dashboard", icon="⚡", default=True)
bills_page = st.Page("pages/3_My_Bills.py", title="My Bills", icon="📄")
what_changed_page = st.Page("pages/4_What_Changed.py", title="What Changed", icon="🔍")
results_page = st.Page("pages/5_Results.py", title="Results & Insights", icon="📊")
forecast_page = st.Page("pages/6_Forecast.py", title="Forecast & Check", icon="🔮")
about_page = st.Page("pages/7_About_Karnataka.py", title="About Karnataka", icon="🏛️")

# Gatekeeper routing:
if not st.session_state.get("user"):
    # When logged out, lock navigation strictly to Login page
    pg = st.navigation([login_page], position="hidden")
else:
    # When logged in, present structured multi-page navigation
    pg = st.navigation({
        "Dashboard": [home_page],
        "Bills & Analysis": [bills_page, what_changed_page, results_page, forecast_page],
        "Reference": [about_page]
    })

# Execute the active page
pg.run()
