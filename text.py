"""
text.py · Bilingual English & Kannada Translations (Complete for all pages)
Function: T(key, lang="en") -> returns translated string
"""

STRINGS = {
    # --- Navigation & Sections ---
    "sec_dashboard": {"en": "Dashboard", "kn": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್"},
    "sec_analysis": {"en": "Bills & Analysis", "kn": "ಬಿಲ್‌ಗಳು ಮತ್ತು ವಿಶ್ಲೇಷಣೆ"},
    "sec_reference": {"en": "Reference & Settings", "kn": "ಮಾಹಿತಿ ಮತ್ತು ಸೆಟ್ಟಿಂಗ್ಸ್"},

    "nav_login": {"en": "Login / Sign Up", "kn": "ಲಾಗ್ ಇನ್ / ಸೈನ್ ಅಪ್"},
    "nav_home": {"en": "Home Dashboard", "kn": "ಮುಖಪುಟ (Home)"},
    "nav_bills": {"en": "My Bills", "kn": "ನನ್ನ ಬಿಲ್‌ಗಳು"},
    "nav_changed": {"en": "What Changed", "kn": "ಏನು ಬದಲಾಗಿದೆ?"},
    "nav_results": {"en": "Results & Insights", "kn": "ಫಲಿತಾಂಶ & ಉಳಿತಾಯ"},
    "nav_forecast": {"en": "Forecast & Check", "kn": "ಮುನ್ಸೂಚನೆ & ತಪಾಸಣೆ"},
    "nav_about": {"en": "About Karnataka", "kn": "ಕರ್ನಾಟಕ ಬೆಸ್ಕಾಂ ಮಾಹಿತಿ"},
    "nav_settings": {"en": "Settings", "kn": "ಸೆಟ್ಟಿಂಗ್ಸ್"},

    # --- Brand & Header ---
    "app_title": {"en": "⚡ Power Bill Coach · Karnataka", "kn": "⚡ ವಿದ್ಯುತ್ ಬಿಲ್ ಕೋಚ್ · ಕರ್ನಾಟಕ"},
    "app_subtitle": {"en": "Karnataka · BESCOM Domestic Advisor", "kn": "ಕರ್ನಾಟಕ · ಬೆಸ್ಕಾಂ ಗೃಹ ವಿದ್ಯುತ್ ಸಲಹೆಗಾರ"},
    "tagline": {"en": "Your BESCOM bill, explained like a friend would. No watts, no appliance lists. Just simple questions.", "kn": "ನಿಮ್ಮ ಬೆಸ್ಕಾಂ ಬಿಲ್ ಅನ್ನು ಸುಲಭವಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ. ಯಾವುದೇ ಕಷ್ಟದ ಲೆಕ್ಕಾಚಾರಗಳಿಲ್ಲ."},
    "no_passwords": {"en": "We never ask for BESCOM passwords. Your data stays safe and local.", "kn": "ನಾವು ಬೆಸ್ಕಾಂ ಪಾಸ್‌ವರ್ಡ್‌ಗಳನ್ನು ಕೇಳುವುದಿಲ್ಲ. ನಿಮ್ಮ ಮಾಹಿತಿ ಸುರಕ್ಷಿತವಾಗಿರುತ್ತದೆ."},

    # --- Sidebar ---
    "sidebar_logged_in": {"en": "Logged In As", "kn": "ಲಾಗಿನ್ ಆಗಿರುವ ಬಳಕೆದಾರ"},
    "sidebar_please_login": {"en": "🔐 Please log in to view your household bills and insights.", "kn": "🔐 ನಿಮ್ಮ ಮನೆಯ ಬಿಲ್ ನೋಡಲು ದಯವಿಟ್ಟು ಲಾಗ್ ಇನ್ ಮಾಡಿ."},
    "sidebar_logout": {"en": "🚪 Log Out", "kn": "🚪 ಲಾಗ್ ಔಟ್"},
    "sidebar_helpline": {"en": "☎️ BESCOM Helpline: 1912", "kn": "☎️ ಬೆಸ್ಕಾಂ ಸಹಾಯವಾಣಿ: 1912"},
    "sidebar_mithra": {"en": "📱 BESCOM Mithra App for official meter complaints", "kn": "📱 ಅಧಿಕೃತ ಮೀಟರ್ ದೂರುಗಳಿಗೆ ಬೆಸ್ಕಾಂ ಮಿತ್ರ ಆ್ಯಪ್"},

    # --- Main Tabs ---
    "tab_login": {"en": "🔑 Log In", "kn": "🔑 ಲಾಗ್ ಇನ್"},
    "tab_signup": {"en": "📝 Create Account", "kn": "📝 ಹೊಸ ಖಾತೆ ರಚಿಸಿ"},
    "tab_settings": {"en": "⚙️ Settings", "kn": "⚙️ ಸೆಟ್ಟಿಂಗ್ಸ್"},

    # --- Sub-tabs inside Settings ---
    "settings_tab_lang": {"en": "🌐 Language", "kn": "🌐 ಭಾಷೆ"},
    "settings_tab_theme": {"en": "🎨 Theme", "kn": "🎨 ಥೀಮ್"},
    "settings_tab_account": {"en": "👤 Account", "kn": "👤 ಖಾತೆ"},

    # --- Settings & Theme Content ---
    "settings_sub": {"en": "Application Settings & Preferences", "kn": "ಅಪ್ಲಿಕೇಶನ್ ಸೆಟ್ಟಿಂಗ್ಸ್ ಮತ್ತು ಆದ್ಯತೆಗಳು"},
    "settings_lang_label": {"en": "Preferred Language / ಭಾಷೆ", "kn": "ಆದ್ಯತೆಯ ಭಾಷೆ / Language"},
    "settings_lang_help": {"en": "Choose your preferred language. All tabs, navigation, and charts will switch instantly.", "kn": "ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ. ಎಲ್ಲಾ ಪುಟಗಳು ತಕ್ಷಣ ಬದಲಾಗುತ್ತವೆ."},
    "theme_title": {"en": "Select Visual Theme", "kn": "ದೃಶ್ಯ ಥೀಮ್ ಆಯ್ಕೆಮಾಡಿ"},
    "theme_desc": {"en": "Choose your preferred color theme. Custom themes can be added here.", "kn": "ನಿಮ್ಮ ಆದ್ಯತೆಯ ಬಣ್ಣದ ಥೀಮ್ ಆಯ್ಕೆಮಾಡಿ. ಕಸ್ಟಮ್ ಥೀಮ್‌ಗಳನ್ನು ಇಲ್ಲಿ ಸೇರಿಸಬಹುದು."},
    "theme_default": {"en": "Karnataka BESCOM (Emerald & Slate)", "kn": "ಕರ್ನಾಟಕ ಬೆಸ್ಕಾಂ (ಹಸಿರು ಮತ್ತು ಕಪ್ಪು)"},
    "theme_coming_soon": {"en": "📸 Ready for custom themes! Provide your reference images anytime to customize this styling.", "kn": "📸 ಕಸ್ಟಮ್ ಥೀಮ್‌ಗಳಿಗೆ ಸಿದ್ಧವಾಗಿದೆ! ಈ ಶೈಲಿಯನ್ನು ಬದಲಿಸಲು ನಿಮ್ಮ ರೆಫರೆನ್ಸ್ ಚಿತ್ರಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಿ."},
    "settings_account_sub": {"en": "Account Information", "kn": "ಖಾತೆ ವಿವರಗಳು"},

    # --- Login Page ---
    "judge_card_title": {"en": "🚀 Quick Access for Judges & Reviewers", "kn": "🚀 ತ್ವರಿತ ಡೆಮೊ ಪ್ರವೇಶ (ಪರಿಶೀಲಕರಿಗೆ)"},
    "judge_card_desc": {"en": "Skip typing and test the full app immediately with 6 pre-loaded sample bills:", "kn": "ಟೈಪ್ ಮಾಡದೆ 6 ಮಾದರಿ ಬಿಲ್‌ಗಳೊಂದಿಗೆ ಅಪ್ಲಿಕೇಶನ್ ತಕ್ಷಣ ಪರೀಕ್ಷಿಸಿ:"},
    "judge_btn": {"en": "⚡ Launch Instant Demo Account", "kn": "⚡ ತ್ವರಿತ ಡೆಮೊ ಖಾತೆ ಪ್ರಾರಂಭಿಸಿ"},
    "login_sub": {"en": "Log in to your account", "kn": "ನಿಮ್ಮ ಖಾತೆಗೆ ಲಾಗ್ ಇನ್ ಮಾಡಿ"},
    "phone_label": {"en": "Mobile Number (10 digits)", "kn": "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ (10 ಅಂಕಿಗಳು)"},
    "phone_placeholder": {"en": "e.g. 9876543210", "kn": "ಉದಾ: 9876543210"},
    "pin_label": {"en": "4-digit Security PIN", "kn": "4-digit Security PIN"},
    "pin_placeholder": {"en": "Enter security PIN / code", "kn": "ಭದ್ರತಾ ಕೋಡ್ ನಮೂದಿಸಿ"},
    "btn_login": {"en": "Log In", "kn": "ಲಾಗ್ ಇನ್ ಮಾಡಿ"},
    "err_phone": {"en": "Please enter a valid 10-digit mobile number.", "kn": "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ 10-ಅಂಕಿಯ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ನಮೂದಿಸಿ."},
    "err_pin": {"en": "Please enter your 4-digit Security PIN.", "kn": "ದಯವಿಟ್ಟು ಭದ್ರತಾ ಪಿನ್ ನಮೂದಿಸಿ."},
    "err_invalid_login": {"en": "Incorrect mobile number or security PIN. Please try again or create an account.", "kn": "ತಪ್ಪಾದ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಅಥವಾ ಭದ್ರತಾ ಪಿನ್. ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ."},

    # --- Sign Up Tab ---
    "signup_sub": {"en": "Create a new account", "kn": "ಹೊಸ ಖಾತೆ ರಚಿಸಿ"},
    "signup_caption": {"en": "Your details are stored strictly in a local database. No BESCOM passwords needed.", "kn": "ನಿಮ್ಮ ವಿವರಗಳು ಸ್ಥಳೀಯ ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಸುರಕ್ಷಿತವಾಗಿರುತ್ತವೆ."},
    "name_label": {"en": "Full Name / Household Name", "kn": "ಪೂರ್ಣ ಹೆಸರು"},
    "name_placeholder": {"en": "e.g. Ramesh Kumar", "kn": "ಉದಾ: ರಮೇಶ್ ಕುಮಾರ್"},
    "pin_confirm_label": {"en": "Confirm 4-digit Security PIN", "kn": "ಭದ್ರತಾ ಪಿನ್ ದೃಢೀಕರಿಸಿ"},
    "btn_signup": {"en": "Create Account", "kn": "ಖಾತೆ ರಚಿಸಿ"},
    "err_name": {"en": "Please enter your name.", "kn": "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹೆಸರನ್ನು ನಮೂದಿಸಿ."},
    "err_pin_match": {"en": "The security PINs do not match. Please re-enter.", "kn": "ಭದ್ರತಾ ಪಿನ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ."},
    "err_user_exists": {"en": "An account with this mobile number already exists. Please log in.", "kn": "ಈ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯ ಖಾತೆ ಈಗಾಗಲೇ ಇದೆ. ದಯವಿಟ್ಟು ಲಾಗ್ ಇನ್ ಮಾಡಿ."},

    # --- Home Dashboard ---
    "welcome": {"en": "Welcome back", "kn": "ಸುಸ್ವಾಗತ"},
    "home_subtitle": {"en": "Here is your household's latest BESCOM electricity overview", "kn": "ನಿಮ್ಮ ಮನೆಯ ಬೆಸ್ಕಾಂ ವಿದ್ಯುತ್ ಖಾತೆಯ ವಿವರಗಳು"},
    "metric_latest_bill": {"en": "Latest Bill to Pay", "kn": "ಇತ್ತೀಚಿನ ಬಿಲ್"},
    "metric_units": {"en": "Units Consumed", "kn": "ಬಳಸಿದ ಯೂನಿಟ್‌ಗಳು"},
    "metric_daily": {"en": "Daily Average", "kn": "ದೈನಂದಿನ ಸರಾಸರಿ"},
    "metric_gj_status": {"en": "Gruha Jyothi Scheme", "kn": "ಗೃಹ ಜ್ಯೋತಿ ಸ್ಥಿತಿ"},
    "gj_free": {"en": "₹0 (Full Free)", "kn": "₹0 (ಸಂಪೂರ್ಣ ಉಚಿತ)"},
    "gj_partial": {"en": "Partly Free", "kn": "ಭಾಗಶಃ ಉಚಿತ"},
    "gj_lost": {"en": "Lost (200+ units)", "kn": "ರದ್ದಾಗಿದೆ (200+ ಯೂನಿಟ್)"},
    "gj_not_enrolled": {"en": "Not Enrolled", "kn": "ನೋಂದಾಯಿಸಿಲ್ಲ"},
    "meter_title": {"en": "🎯 Gruha Jyothi 200-Unit Safety Meter", "kn": "🎯 ಗೃಹ ಜ್ಯೋತಿ 200-ಯೂನಿಟ್ ಸುರಕ್ಷತಾ ಮೀಟರ್"},
    "meter_caption": {"en": "In Karnataka, keeping your monthly usage under 200 units keeps your subsidized rate active.", "kn": "ಕರ್ನಾಟಕದಲ್ಲಿ, ಮಾಸಿಕ ಬಳಕೆಯನ್ನು 200 ಯೂನಿಟ್‌ಗಳ ಒಳಗೆ ಇಡುವುದು ಉಚಿತ ಸೌಲಭ್ಯವನ್ನು ಕಾಪಾಡುತ್ತದೆ."},
    "units_buffer": {"en": "Buffer left before losing ₹0 scheme:", "kn": "ಉಚಿತ ಸೌಲಭ್ಯ ಉಳಿಸಿಕೊಳ್ಳಲು ಬಾಕಿ ಯೂನಿಟ್‌ಗಳು:"},
    "units_over": {"en": "Over the line! Full bill payable:", "kn": "200 ಯೂನಿಟ್ ಮೀರಿದೆ! ಪೂರ್ಣ ಬಿಲ್ ಪಾವತಿಸಬೇಕು:"},
    "quick_nav": {"en": "⚡ Quick Navigation", "kn": "⚡ ತ್ವರಿತ ಪುಟಗಳು"},
    "nav_bills_desc": {"en": "View bill history, add new monthly bills, or manage records.", "kn": "ಹಿಂದಿನ ಬಿಲ್‌ಗಳನ್ನು ವೀಕ್ಷಿಸಿ, ಹೊಸ ಬಿಲ್ ಸೇರಿಸಿ ಅಥವಾ ನಿರ್ವಹಿಸಿ."},
    "nav_changed_desc": {"en": "Answer simple questions about guests, vacations, heat, or motors.", "kn": "ಅತಿಥಿಗಳು, ರಜೆ, ಬಿಸಿಲು ಅಥವಾ ಮೋಟಾರ್ ಬಳಕೆಯ ಬಗ್ಗೆ ಉತ್ತರಿಸಿ."},
    "nav_results_desc": {"en": "See waterfall breakdown, vacation tests, and tailored saving tips.", "kn": "ಬಿಲ್ ಹೆಚ್ಚಳದ ಕಾರಣಗಳು, ನಷ್ಟದ ತಪಾಸಣೆ ಮತ್ತು ಉಳಿತಾಯದ ಸಲಹೆಗಳು."},
    "nav_forecast_desc": {"en": "Project next month's bill, simulate fuel shocks, and mid-month test.", "kn": "ಮುಂದಿನ ತಿಂಗಳ ಬಿಲ್ ಲೆಕ್ಕಾಚಾರ ಮತ್ತು ಅರ್ಧ ತಿಂಗಳ ಮೀಟರ್ ಪರಿಶೀಲನೆ."},

    # --- Page 3: My Bills ---
    "bills_title": {"en": "📄 My Bills · Electricity History", "kn": "📄 ನನ್ನ ಬಿಲ್‌ಗಳು · ವಿದ್ಯುತ್ ಬಿಲ್ ಇತಿಹಾಸ"},
    "bills_caption": {"en": "Keep track of your monthly BESCOM units and charges. At least two bills are needed to explain jumps.", "kn": "ನಿಮ್ಮ ಮಾಸಿಕ ಬೆಸ್ಕಾಂ ಯೂನಿಟ್‌ಗಳು ಮತ್ತು ಶುಲ್ಕಗಳನ್ನು ದಾಖಲಿಸಿ. ಬಿಲ್ ಹೆಚ್ಚಳ ತಿಳಿಯಲು ಕನಿಷ್ಠ 2 ಬಿಲ್‌ಗಳು ಬೇಕು."},
    "bills_add_expander": {"en": "➕ Add a New Monthly Bill", "kn": "➕ ಹೊಸ ಮಾಸಿಕ ಬಿಲ್ ಸೇರಿಸಿ"},
    "bill_month_label": {"en": "Billing Month / Label", "kn": "ಬಿಲ್ಲಿಂಗ್ ತಿಂಗಳು / ಹೆಸರು"},
    "bill_units_label": {"en": "Units Consumed (kWh)", "kn": "ಬಳಸಿದ ಯೂನಿಟ್‌ಗಳು (kWh)"},
    "bill_days_label": {"en": "Billing Days in Cycle", "kn": "ಬಿಲ್ಲಿಂಗ್ ದಿನಗಳು"},
    "bill_est_label": {"en": "Estimated Reading? (Door lock / meter not read)", "kn": "ಅಂದಾಜು ರೀಡಿಂಗ್? (ಬಾಗಿಲು ಹಾಕಲಾಗಿತ್ತು / ಮೀಟರ್ ಓದಲಾಗಿಲ್ಲ)"},
    "bill_kw_label": {"en": "Sanctioned Load (kW)", "kn": "ಮಂಜೂರಾದ ಲೋಡ್ (kW)"},
    "bill_gj_enrolled": {"en": "Enrolled in Gruha Jyothi", "kn": "ಗೃಹ ಜ್ಯೋತಿ ಯೋಜನೆ ನೋಂದಾಯಿಸಲಾಗಿದೆ"},
    "bill_free_label": {"en": "Free Units Printed on Bill", "kn": "ಬಿಲ್‌ನಲ್ಲಿ ಮುದ್ರಿಸಲಾದ ಉಚಿತ ಯೂನಿಟ್‌ಗಳು"},
    "bill_fuel_label": {"en": "Fuel Surcharge / FPPCA (₹/unit)", "kn": "ಇಂಧನ ಹೊಂದಾಣಿಕೆ ಶುಲ್ಕ FPPCA (₹/ಯೂನಿಟ್)"},
    "bill_save_btn": {"en": "Save Bill Record", "kn": "ಬಿಲ್ ದಾಖಲೆ ಉಳಿಸಿ"},
    "bills_saved_sub": {"en": "Saved Bills", "kn": "ಉಳಿಸಲಾದ ಬಿಲ್‌ಗಳು"},
    "bills_delete_sub": {"en": "🗑️ Delete a Bill", "kn": "🗑️ ಬಿಲ್ ಅಳಿಸಿ"},
    "bills_del_btn": {"en": "Confirm Delete", "kn": "ಅಳಿಸಲು ಖಚಿತಪಡಿಸಿ"},

    # --- Page 4: What Changed ---
    "changed_title": {"en": "🔍 What Changed This Month?", "kn": "🔍 ಈ ತಿಂಗಳು ಏನು ಬದಲಾಗಿದೆ?"},
    "changed_caption": {"en": "Tell us what was different in your household during this billing cycle. No technical wattage questions!", "kn": "ಈ ತಿಂಗಳು ನಿಮ್ಮ ಮನೆಯಲ್ಲಿ ಏನು ಬದಲಾವಣೆ ಆಯಿತು ಎಂದು ತಿಳಿಸಿ. ಯಾವುದೇ ಕಷ್ಟದ ಪ್ರಶ್ನೆಗಳಿಲ್ಲ!"},
    "changed_travel_sub": {"en": "🏖️ Travel & Guests", "kn": "🏖️ ಪ್ರವಾಸ ಮತ್ತು ಅತಿಥಿಗಳು"},
    "changed_vacation": {"en": "Days nobody was home (vacation / away)", "kn": "ಮನೆಯಲ್ಲಿ ಯಾರೂ ಇರದ ದಿನಗಳು (ರಜೆ / ಪ್ರವಾಸ)"},
    "changed_guests": {"en": "How many guests stayed over? (0 if none)", "kn": "ಎಷ್ಟು ಅತಿಥಿಗಳು ಉಳಿದುಕೊಂಡಿದ್ದರು? (ಇಲ್ಲದಿದ್ದರೆ 0)"},
    "changed_guest_days": {"en": "For how many days did guests stay?", "kn": "ಅತಿಥಿಗಳು ಎಷ್ಟು ದಿನ ಉಳಿದುಕೊಂಡಿದ್ದರು?"},
    "changed_weather_sub": {"en": "🌡️ Weather & Seasons", "kn": "🌡️ ಹವಾಮಾನ ಮತ್ತು ಋತುಗಳು"},
    "changed_heat": {"en": "It was hot / summer, and we used AC / cooler / fans more", "kn": "ಬಿಸಿಲಿದ್ದ ಕಾರಣ AC / ಕೂಲರ್ / ಫ್ಯಾನ್ ಹೆಚ್ಚು ಬಳಸಿದೆವು"},
    "changed_geyser": {"en": "It was rainy / cold, and we ran the geyser / water heater more", "kn": "ಚಳಿಯಿದ್ದ ಕಾರಣ ಗೀಸರ್ / ಹೀಟರ್ ಹೆಚ್ಚು ಬಳಸಿದೆವು"},
    "changed_habits_sub": {"en": "🏠 Home Habits & Appliances", "kn": "🏠 ಮನೆಯ ಅಭ್ಯಾಸಗಳು ಮತ್ತು ಉಪಕರಣಗಳು"},
    "changed_home_more": {"en": "More people stayed home during the daytime (holidays / WFH)", "kn": "ಹಗಲಿನಲ್ಲಿ ಹೆಚ್ಚು ಜನರು ಮನೆಯಲ್ಲಿದ್ದರು (ರಜೆ / WFH)"},
    "changed_pump": {"en": "Water motor / borehole pump ran more often (water shortage / overflow)", "kn": "ನೀರಿನ ಮೋಟಾರ್ / ಪಂಪ್ ಹೆಚ್ಚು ಸಮಯ ಓಡಿತು"},
    "changed_fest": {"en": "Put up decorative festival lighting (Dasara / Diwali / Ramadan)", "kn": "ಹಬ್ಬದ ದೀಪಾಲಂಕಾರ ಮಾಡಲಾಗಿತ್ತು (ದಸರಾ / ದೀಪಾವಳಿ)"},
    "changed_power_cuts": {"en": "Frequent power cuts / inverter ran extra charge cycles", "kn": "ವಿದ್ಯುತ್ ಕಡಿತ / ಇನ್ವರ್ಟರ್ ಹೆಚ್ಚು ಚಾರ್ಜ್ ಆಯಿತು"},
    "changed_new_items": {"en": "Did you purchase or start using any new appliances?", "kn": "ಯಾವುದಾದರೂ ಹೊಸ ವಿದ್ಯುತ್ ಉಪಕರಣ ಖರೀದಿಸಿದ್ದೀರಾ?"},
    "changed_submit_btn": {"en": "Analyze My Bill Jump →", "kn": "ಬಿಲ್ ಹೆಚ್ಚಳವನ್ನು ವಿಶ್ಲೇಷಿಸಿ →"},

    # --- Page 5: Results & Insights ---
    "results_title": {"en": "📊 Diagnostic Results & Bill Jump Analysis", "kn": "📊 ಬಿಲ್ ಹೆಚ್ಚಳದ ಕಾರಣಗಳು ಮತ್ತು ವಿಶ್ಲೇಷಣೆ"},
    "results_caption": {"en": "Here is the exact decomposition of why your bill changed and how to eliminate waste.", "kn": "ನಿಮ್ಮ ಬಿಲ್ ಏಕೆ ಹೆಚ್ಚಾಗಿದೆ ಮತ್ತು ಅನಗತ್ಯ ವಿದ್ಯುತ್ ವ್ಯರ್ಥ ತಪ್ಪಿಸುವುದು ಹೇಗೆ ಎಂಬ ವಿವರ ಇಲ್ಲಿದೆ."},
    "card1_sub": {"en": "1 · Why your bill changed", "kn": "1 · ನಿಮ್ಮ ಬಿಲ್ ಏಕೆ ಬದಲಾಯಿತು?"},
    "card1_net_jump": {"en": "Net Jump:", "kn": "ಒಟ್ಟು ಬದಲಾವಣೆ:"},
    "card2_sub": {"en": "2 · Where the waste is (Audits & Leakage)", "kn": "2 · ವಿದ್ಯುತ್ ವ್ಯರ್ಥ ಎಲ್ಲಿದೆ? (ತಪಾಸಣೆ)"},
    "card3_sub": {"en": "3 · How to save on next bill", "kn": "3 · ಮುಂದಿನ ಬಿಲ್‌ನಲ್ಲಿ ಉಳಿತಾಯ ಮಾಡುವುದು ಹೇಗೆ?"},

    # --- Page 6: Forecast & Check ---
    "forecast_title": {"en": "🔮 Next Month Forecast & Mid-Month Check", "kn": "🔮 ಮುಂದಿನ ತಿಂಗಳ ಬಿಲ್ ಮುನ್ಸೂಚನೆ & ಅರ್ಧ-ತಿಂಗಳ ತಪಾಸಣೆ"},
    "forecast_caption": {"en": "Plan your power consumption ahead, prevent fuel price shocks, and check your mid-month pace.", "kn": "ನಿಮ್ಮ ವಿದ್ಯುತ್ ಬಳಕೆಯನ್ನು ಯೋಜಿಸಿ, ದರ ಏರಿಕೆಯ ಆಘಾತ ತಪ್ಪಿಸಿ ಮತ್ತು ಮೀಟರ್ ವೇಗ ಪರಿಶೀಲಿಸಿ."},
    "forecast_q_sub": {"en": "1 · Forecast Questions for Next Month", "kn": "1 · ಮುಂದಿನ ತಿಂಗಳ ಯೋಜನೆಗಳು"},
    "forecast_away": {"en": "Days you will be away next month", "kn": "ಮುಂದಿನ ತಿಂಗಳು ನೀವು ಊರಿನಲ್ಲಿ ಇರದ ದಿನಗಳು"},
    "forecast_guests": {"en": "Extra guests expected next month", "kn": "ಮುಂದಿನ ತಿಂಗಳು ನಿರೀಕ್ಷಿತ ಅತಿಥಿಗಳ ಸಂಖ್ಯೆ"},
    "forecast_summer": {"en": "Summer season (Mar to May)", "kn": "ಬೇಸಿಗೆ ಕಾಲ (ಮಾರ್ಚ್ - ಮೇ)"},
    "forecast_fuel_sub": {"en": "2 · Fuel Price Simulator", "kn": "2 · ಇಂಧನ ದರ ಸಿಮ್ಯುಲೇಟರ್ (FPPCA)"},
    "forecast_fuel_label": {"en": "Simulated Fuel Surcharge / FPPCA (₹/unit)", "kn": "ಅಂದಾಜು ಇಂಧನ ಹೊಂದಾಣಿಕೆ ಶುಲ್ಕ (₹/ಯೂನಿಟ್)"},
    "forecast_fuel_help": {"en": "Try ₹1.00 to see what an energy cost increase does to your bill even if you use the same power.", "kn": "ಬಳಕೆ ಬದಲಾಗದಿದ್ದರೂ ಇಂಧನ ದರ ಹೆಚ್ಚಾದರೆ ಬಿಲ್ ಹೇಗೆ ಹೆಚ್ಚಾಗುತ್ತದೆ ಎಂದು ನೋಡಲು ₹1.00 ಪ್ರಯತ್ನಿಸಿ."},
    "forecast_est_bill": {"en": "Estimated Bill:", "kn": "ಅಂದಾಜು ಬಿಲ್:"},
    "forecast_likely": {"en": "Most likely", "kn": "ಸಾಧ್ಯವಿರುವ ಮೊತ್ತ"},
    "forecast_risk_high": {"en": "⚠️ High Risk: Your upper projection crosses 200 units. Aim to stay below 6.7 units/day to protect Gruha Jyothi!", "kn": "⚠️ ಅಧಿಕ ಅಪಾಯ: ನಿಮ್ಮ ಬಳಕೆ 200 ಯೂನಿಟ್ ಮೀರಬಹುದು. ಗೃಹ ಜ್ಯೋತಿ ಉಳಿಸಿಕೊಳ್ಳಲು ದಿನಕ್ಕೆ 6.7 ಯೂನಿಟ್‌ಗಳ ಒಳಗೆ ಇರಿಸಿ!"},
    "forecast_mid_sub": {"en": "⚡ Mid-Month Pacing Check (Read Your Meter Today)", "kn": "⚡ ಅರ್ಧ-ತಿಂಗಳ ತಪಾಸಣೆ (ಇಂದೇ ಮೀಟರ್ ರೀಡಿಂಗ್ ನೋಡಿ)"},
    "forecast_mid_desc": {"en": "Check your meter around day 15 of your cycle to avoid sudden surprises:", "kn": "ತಿಂಗಳ ಮಧ್ಯದಲ್ಲಿ (15ನೇ ದಿನ) ಮೀಟರ್ ಪರಿಶೀಲಿಸಿ ಬಿಲ್ ಆಘಾತವನ್ನು ತಪ್ಪಿಸಿ:"},
    "forecast_units_used": {"en": "Units used so far since last bill", "kn": "ಕಳೆದ ಬಿಲ್‌ನಿಂದ ಇದುವರೆಗೆ ಬಳಸಲಾದ ಯೂನಿಟ್‌ಗಳು"},
    "forecast_days_passed": {"en": "Days elapsed since last bill", "kn": "ಕಳೆದ ಬಿಲ್‌ನಿಂದ ಇದುವರೆಗೆ ಕಳೆದಿರುವ ದಿನಗಳು"},
    "forecast_paced_usage": {"en": "Paced Monthly Consumption:", "kn": "ಈ ತಿಂಗಳ ಅಂದಾಜು ಒಟ್ಟು ಬಳಕೆ:"},
    "forecast_lose_gj": {"en": "🚨 At this pace, you will exceed 200 units and LOSE Gruha Jyothi! Keep usage under daily target.", "kn": "🚨 ಈ ವೇಗದಲ್ಲಿ ಮುಂದುವರೆದರೆ 200 ಯೂನಿಟ್ ಮೀರಿ ಗೃಹ ಜ್ಯೋತಿ ರದ್ದಾಗುತ್ತದೆ! ದೈನಂದಿನ ಬಳಕೆಯನ್ನು ಕಡಿಮೆ ಮಾಡಿ."},
    "forecast_on_track": {"en": "✅ On track! At this pace, you are safely within your quota.", "kn": "✅ ಸುರಕ್ಷಿತವಾಗಿದೆ! ಈ ವೇಗದಲ್ಲಿ ನಿಮ್ಮ ಬಳಕೆ ಮಿತಿಯೊಳಗಿರುತ್ತದೆ."},

    # --- Page 7: About Karnataka ---
    "about_title": {"en": "🏛️ About Karnataka Power & BESCOM Tariff Guide", "kn": "🏛️ ಕರ್ನಾಟಕ ವಿದ್ಯುತ್ ಮತ್ತು ಬೆಸ್ಕಾಂ ದರಪಟ್ಟಿ ಮಾರ್ಗದರ್ಶಿ"},
    "about_caption": {"en": "Understanding Karnataka's electricity regulations, the Gruha Jyothi scheme, and tariff calculations.", "kn": "ಕರ್ನಾಟಕದ ವಿದ್ಯುತ್ ನಿಯಮಗಳು, ಗೃಹ ಜ್ಯೋತಿ ಯೋಜನೆ ಮತ್ತು ದರ ಲೆಕ್ಕಾಚಾರಗಳ ವಿವರ."},
    "about_tariff_sub": {"en": "1 · Domestic Tariff Structure (BESCOM LT-2)", "kn": "1 · ಗೃಹ ವಿದ್ಯುತ್ ದರಪಟ್ಟಿ (ಬೆಸ್ಕಾಂ LT-2)"},
    "about_flat_energy": {"en": "Flat Energy Charge", "kn": "ಯೂನಿಟ್ ದರ (ಫ್ಲಾಟ್)"},
    "about_fixed_charge": {"en": "Fixed Charge", "kn": "ಸ್ಥಿರ ಶುಲ್ಕ (Fixed Charge)"},
    "about_tax": {"en": "State Electricity Duty", "kn": "ರಾಜ್ಯ ವಿದ್ಯುತ್ ಶುಲ್ಕ (ತೆರಿಗೆ)"},
    "about_gj_sub": {"en": "2 · How the Gruha Jyothi Scheme Works", "kn": "2 · ಗೃಹ ಜ್ಯೋತಿ ಯೋಜನೆ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ?"},
    "about_escoms_sub": {"en": "3 · Karnataka ESCOMs Overview", "kn": "3 · ಕರ್ನಾಟಕದ ವಿದ್ಯುತ್ ಸರಬರಾಜು ಕಂಪನಿಗಳು (ESCOMs)"}
}


def T(key: str, lang: str = "en") -> str:
    """Team-standard function for retrieving localized text."""
    if not lang or lang not in ("en", "kn"):
        lang = "en"
    entry = STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))
