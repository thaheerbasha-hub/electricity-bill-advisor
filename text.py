"""
text.py · Bilingual English & Kannada Translations (Team Standard)
Function: T(key, lang="en") -> returns translated string
"""

STRINGS = {
    # --- Brand & Header ---
    "app_title": {
        "en": "⚡ Power Bill Coach · Karnataka",
        "kn": "⚡ ವಿದ್ಯುತ್ ಬಿಲ್ ಕೋಚ್ · ಕರ್ನಾಟಕ"
    },
    "app_subtitle": {
        "en": "Karnataka · BESCOM Domestic Advisor",
        "kn": "ಕರ್ನಾಟಕ · ಬೆಸ್ಕಾಂ ಗೃಹ ವಿದ್ಯುತ್ ಸಲಹೆಗಾರ"
    },
    "tagline": {
        "en": "Your BESCOM bill, explained like a friend would. No watts, no appliance lists. Just simple questions.",
        "kn": "ನಿಮ್ಮ ಬೆಸ್ಕಾಂ ಬಿಲ್ ಅನ್ನು ಸ್ನೇಹಿತನಂತೆ ಸುಲಭವಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ. ಯಾವುದೇ ಕಷ್ಟದ ಲೆಕ್ಕಾಚಾರಗಳಿಲ್ಲ."
    },
    "no_passwords": {
        "en": "We never ask for BESCOM passwords. Your data stays safe and local.",
        "kn": "ನಾವು ಬೆಸ್ಕಾಂ ಪಾಸ್‌ವರ್ಡ್‌ಗಳನ್ನು ಕೇಳುವುದಿಲ್ಲ. ನಿಮ್ಮ ಮಾಹಿತಿ ಸುರಕ್ಷಿತವಾಗಿರುತ್ತದೆ."
    },

    # --- Sidebar ---
    "sidebar_logged_in": {
        "en": "Logged In As",
        "kn": "ಲಾಗಿನ್ ಆಗಿರುವ ಬಳಕೆದಾರ"
    },
    "sidebar_please_login": {
        "en": "🔐 Please log in to view your household bills and insights.",
        "kn": "🔐 ನಿಮ್ಮ ಮನೆಯ ಬಿಲ್ ಮತ್ತು ವಿವರಗಳನ್ನು ವೀಕ್ಷಿಸಲು ದಯವಿಟ್ಟು ಲಾಗ್ ಇನ್ ಮಾಡಿ."
    },
    "sidebar_lang_label": {
        "en": "Language / ಭಾಷೆ",
        "kn": "ಭಾಷೆ / Language"
    },
    "sidebar_logout": {
        "en": "🚪 Log Out",
        "kn": "🚪 ಲಾಗ್ ಔಟ್"
    },
    "sidebar_helpline": {
        "en": "☎️ BESCOM Helpline: 1912",
        "kn": "☎️ ಬೆಸ್ಕಾಂ ಸಹಾಯವಾಣಿ: 1912"
    },
    "sidebar_mithra": {
        "en": "📱 BESCOM Mithra App for official meter complaints",
        "kn": "📱 ಅಧಿಕೃತ ಮೀಟರ್ ದೂರುಗಳಿಗಾಗಿ ಬೆಸ್ಕಾಂ ಮಿತ್ರ ಆ್ಯಪ್"
    },

    # --- Login Page ---
    "judge_card_title": {
        "en": "🚀 Quick Access for Judges & Reviewers",
        "kn": "🚀 ತ್ವರಿತ ಡೆಮೊ ಪ್ರವೇಶ (ಪರಿಶೀಲಕರಿಗೆ)"
    },
    "judge_card_desc": {
        "en": "Skip typing and test the full app immediately with 6 pre-loaded sample bills:",
        "kn": "ಟೈಪ್ ಮಾಡದೆ 6 ಮಾದರಿ ಬಿಲ್‌ಗಳೊಂದಿಗೆ ಅಪ್ಲಿಕೇಶನ್ ತಕ್ಷಣ ಪರೀಕ್ಷಿಸಿ:"
    },
    "judge_btn": {
        "en": "⚡ Launch Instant Demo Account",
        "kn": "⚡ ತ್ವರಿತ ಡೆಮೊ ಖಾತೆ ಪ್ರಾರಂಭಿಸಿ"
    },
    "tab_login": {
        "en": "🔑 Log In",
        "kn": "🔑 ಲಾಗ್ ಇನ್"
    },
    "tab_signup": {
        "en": "📝 Create Account",
        "kn": "📝 ಹೊಸ ಖಾತೆ ರಚಿಸಿ"
    },
    "login_sub": {
        "en": "Log in to your account",
        "kn": "ನಿಮ್ಮ ಖಾತೆಗೆ ಲಾಗ್ ಇನ್ ಮಾಡಿ"
    },
    "phone_label": {
        "en": "Mobile Number (10 digits)",
        "kn": "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ (10 ಅಂಕಿಗಳು)"
    },
    "phone_placeholder": {
        "en": "e.g. 9876543210",
        "kn": "ಉದಾ: 9876543210"
    },
    "pin_label": {
        "en": "4-digit Security PIN",
        "kn": "4-digit Security PIN"
    },
    "pin_placeholder": {
        "en": "Enter security PIN / code",
        "kn": "ಭದ್ರತಾ ಕೋಡ್ ನಮೂದಿಸಿ"
    },
    "btn_login": {
        "en": "Log In",
        "kn": "ಲಾಗ್ ಇನ್ ಮಾಡಿ"
    },
    "err_phone": {
        "en": "Please enter a valid 10-digit mobile number.",
        "kn": "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ 10-ಅಂಕಿಯ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ನಮೂದಿಸಿ."
    },
    "err_pin": {
        "en": "Please enter your 4-digit Security PIN.",
        "kn": "ದಯವಿಟ್ಟು ಭದ್ರತಾ ಪಿನ್ ನಮೂದಿಸಿ."
    },
    "err_invalid_login": {
        "en": "Incorrect mobile number or security PIN. Please try again or create an account.",
        "kn": "ತಪ್ಪಾದ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಅಥವಾ ಭದ್ರತಾ ಪಿನ್. ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ."
    },

    # --- Sign Up Tab ---
    "signup_sub": {
        "en": "Create a new account",
        "kn": "ಹೊಸ ಖಾತೆ ರಚಿಸಿ"
    },
    "signup_caption": {
        "en": "Your details are stored strictly in a local database. No BESCOM passwords needed.",
        "kn": "ನಿಮ್ಮ ವಿವರಗಳು ಸ್ಥಳೀಯ ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಸುರಕ್ಷಿತವಾಗಿರುತ್ತವೆ."
    },
    "name_label": {
        "en": "Full Name / Household Name",
        "kn": "ಪೂರ್ಣ ಹೆಸರು"
    },
    "name_placeholder": {
        "en": "e.g. Ramesh Kumar",
        "kn": "ಉದಾ: ರಮೇಶ್ ಕುಮಾರ್"
    },
    "pin_confirm_label": {
        "en": "Confirm 4-digit Security PIN",
        "kn": "ಭದ್ರತಾ ಪಿನ್ ದೃಢೀಕರಿಸಿ"
    },
    "btn_signup": {
        "en": "Create Account",
        "kn": "ಖಾತೆ ರಚಿಸಿ"
    },
    "err_name": {
        "en": "Please enter your name.",
        "kn": "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹೆಸರನ್ನು ನಮೂದಿಸಿ."
    },
    "err_pin_match": {
        "en": "The security PINs do not match. Please re-enter.",
        "kn": "ಭದ್ರತಾ ಪಿನ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ."
    },
    "err_user_exists": {
        "en": "An account with this mobile number already exists. Please log in.",
        "kn": "ಈ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯ ಖಾತೆ ಈಗಾಗಲೇ ಇದೆ. ದಯವಿಟ್ಟು ಲಾಗ್ ಇನ್ ಮಾಡಿ."
    },

    # --- Home Dashboard ---
    "welcome": {
        "en": "Welcome back",
        "kn": "ಸುಸ್ವಾಗತ"
    },
    "home_subtitle": {
        "en": "Here is your household's latest BESCOM electricity overview",
        "kn": "ನಿಮ್ಮ ಮನೆಯ ಬೆಸ್ಕಾಂ ವಿದ್ಯುತ್ ಖಾತೆಯ ವಿವರಗಳು"
    },
    "metric_latest_bill": {
        "en": "Latest Bill to Pay",
        "kn": "ಇತ್ತೀಚಿನ ಬಿಲ್"
    },
    "metric_units": {
        "en": "Units Consumed",
        "kn": "ಬಳಸಿದ ಯೂನಿಟ್‌ಗಳು"
    },
    "metric_daily": {
        "en": "Daily Average",
        "kn": "ದೈನಂದಿನ ಸರಾಸರಿ"
    },
    "metric_gj_status": {
        "en": "Gruha Jyothi Scheme",
        "kn": "ಗೃಹ ಜ್ಯೋತಿ ಸ್ಥಿತಿ"
    },
    "gj_free": {
        "en": "₹0 (Full Free)",
        "kn": "₹0 (ಸಂಪೂರ್ಣ ಉಚಿತ)"
    },
    "gj_partial": {
        "en": "Partly Free",
        "kn": "ಭಾಗಶಃ ಉಚಿತ"
    },
    "gj_lost": {
        "en": "Lost (200+ units)",
        "kn": "ರದ್ದಾಗಿದೆ (200+ ಯೂನಿಟ್)"
    },
    "gj_not_enrolled": {
        "en": "Not Enrolled",
        "kn": "ನೋಂದಾಯಿಸಿಲ್ಲ"
    },
    "meter_title": {
        "en": "🎯 Gruha Jyothi 200-Unit Safety Meter",
        "kn": "🎯 ಗೃಹ ಜ್ಯೋತಿ 200-ಯೂನಿಟ್ ಸುರಕ್ಷತಾ ಮೀಟರ್"
    },
    "meter_caption": {
        "en": "In Karnataka, keeping your monthly usage under 200 units keeps your subsidized rate active.",
        "kn": "ಕರ್ನಾಟಕದಲ್ಲಿ, ಮಾಸಿಕ ಬಳಕೆಯನ್ನು 200 ಯೂನಿಟ್‌ಗಳ ಒಳಗೆ ಇಡುವುದು ನಿಮ್ಮ ಉಚಿತ ಸೌಲಭ್ಯವನ್ನು ಕಾಪಾಡುತ್ತದೆ."
    },
    "units_buffer": {
        "en": "Buffer left before losing ₹0 scheme:",
        "kn": "ಉಚಿತ ಸೌಲಭ್ಯ ಉಳಿಸಿಕೊಳ್ಳಲು ಬಾಕಿ ಯೂನಿಟ್‌ಗಳು:"
    },
    "units_over": {
        "en": "Over the line! Full bill payable:",
        "kn": "200 ಯೂನಿಟ್ ಮೀರಿದೆ! ಪೂರ್ಣ ಬಿಲ್ ಪಾವತಿಸಬೇಕು:"
    },
    "quick_nav": {
        "en": "⚡ Quick Navigation",
        "kn": "⚡ ತ್ವರಿತ ಪುಟಗಳು"
    },
    "nav_bills": {
        "en": "📄 My Bills",
        "kn": "📄 ನನ್ನ ಬಿಲ್‌ಗಳು"
    },
    "nav_bills_desc": {
        "en": "View bill history, add new monthly bills, or manage records.",
        "kn": "ಹಿಂದಿನ ಬಿಲ್‌ಗಳನ್ನು ವೀಕ್ಷಿಸಿ, ಹೊಸ ಬಿಲ್ ಸೇರಿಸಿ ಅಥವಾ ನಿರ್ವಹಿಸಿ."
    },
    "nav_changed": {
        "en": "🔍 What Changed",
        "kn": "🔍 ಏನಾಯಿತು?"
    },
    "nav_changed_desc": {
        "en": "Answer simple questions about guests, vacations, heat, or motors.",
        "kn": "ಅತಿಥಿಗಳು, ರಜೆ, ಬಿಸಿಲು ಅಥವಾ ಮೋಟಾರ್ ಬಳಕೆಯ ಬಗ್ಗೆ ಉತ್ತರಿಸಿ."
    },
    "nav_results": {
        "en": "📊 Results & Waste",
        "kn": "📊 ಫಲಿತಾಂಶ ಮತ್ತು ಉಳಿತಾಯ"
    },
    "nav_results_desc": {
        "en": "See waterfall breakdown, vacation tests, and tailored saving tips.",
        "kn": "ಬಿಲ್ ಹೆಚ್ಚಳದ ಕಾರಣಗಳು, ನಷ್ಟದ ತಪಾಸಣೆ ಮತ್ತು ಉಳಿತಾಯದ ಸಲಹೆಗಳು."
    },
    "nav_forecast": {
        "en": "🔮 Next Forecast",
        "kn": "🔮 ಮುಂದಿನ ಬಿಲ್ ಮುನ್ಸೂಚನೆ"
    },
    "nav_forecast_desc": {
        "en": "Project next month's bill, simulate fuel shocks, and mid-month test.",
        "kn": "ಮುಂದಿನ ತಿಂಗಳ ಬಿಲ್ ಲೆಕ್ಕಾಚಾರ ಮತ್ತು ಅರ್ಧ ತಿಂಗಳ ಮೀಟರ್ ಪರಿಶೀಲನೆ."
    }
}


def T(key: str, lang: str = "en") -> str:
    """Team-standard function for retrieving localized text."""
    if not lang or lang not in ("en", "kn"):
        lang = "en"
    entry = STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))
