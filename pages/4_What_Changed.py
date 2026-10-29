"""
pages/4_What_Changed.py · What Changed This Month?
Assigned to: RISHABH (HackNova-26, Problem P01)

Features:
  - Renders QUESTIONS for the latest bill (vacations, guests, heat/AC, geyser, motor, new items, festival lights, power cuts)
  - Interactive, unlocked controls for immediate selection
  - Saves answers to st.session_state['answers']
  - Seamless navigation to Results
  - Fully bilingual (English / Kannada via text.T) and themed with ui_common
"""

import streamlit as st
import db
import ui_common
import text
import questions

# Ensure user dict compatibility for ui_common
if isinstance(st.session_state.get("user"), dict):
    st.session_state["user"].setdefault("name", st.session_state["user"].get("id", "User"))

# Apply global styling and persistent sidebar
ui_common.apply_custom_css()
ui_common.render_sidebar()

# Session State Conventions
if "user" not in st.session_state:
    st.session_state["user"] = None
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
if "answers" not in st.session_state:
    st.session_state["answers"] = {}

lang = st.session_state.get("lang", "en")
user = st.session_state.get("user")

# Header
title_text = text.T("changed_title", lang)
if title_text == "changed_title":
    title_text = "What Changed This Month?"
st.title(title_text)

caption_text = text.T("changed_caption", lang)
if caption_text == "changed_caption":
    caption_text = "Nobody counts watts or reads appliance labels. Just answer simple questions about what was different this billing cycle."
st.caption(caption_text)

# -----------------------------------------------------------------------------
# User & Bills Check (Friendly messages, must not crash)
# -----------------------------------------------------------------------------
if not user:
    st.info("👋 " + ("Browsing as guest. You can fill out these questions to test the diagnosis. Log in anytime in Login / Sign Up to link your bills." if lang == "en" else "ಅತಿಥಿಯಾಗಿ ವೀಕ್ಷಿಸುತ್ತಿದ್ದೀರಿ. ಬಿಲ್‌ಗಳನ್ನು ಉಳಿಸಲು ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ."))
    user_id = "demo_user"
else:
    user_id = user.get("id", "demo_user") if isinstance(user, dict) else str(user)
    user_name = user.get("name", user_id) if isinstance(user, dict) else user_id
    st.caption(f"👤 Account: **{user_name}**")

try:
    bills = db.get_bills(user_id)
except Exception:
    bills = st.session_state.get("bills", [])

if not bills:
    st.warning(
        "📋 " + ("No bills saved yet. You can add your bills in **My Bills** anytime. You can still answer the questions below to test your waste checks and savings tips."
                 if lang == "en" else
                 "ಇನ್ನೂ ಯಾವುದೇ ಬಿಲ್‌ಗಳು ದಾಖಲಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು **ನನ್ನ ಬಿಲ್‌ಗಳು** ಪುಟದಲ್ಲಿ ಬಿಲ್ ಸೇರಿಸಿ. ಕೆಳಗಿನ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ ಉಳಿತಾಯ ಸಲಹೆಗಳನ್ನು ನೋಡಬಹುದು.")
    )
elif len(bills) == 1:
    b = bills[0]
    st.info(f"📋 Answering for bill: **{b.get('month', 'Current')}** · **{b.get('units', 0.0):.0f} units** · **{b.get('days', 30)} days**.")
else:
    cur = bills[-1]
    prev = bills[-2]
    st.info(
        f"Comparing current bill (**{cur.get('month', 'Latest')}**: {cur.get('units', 0.0):.0f} units, {cur.get('days', 30)} days) "
        f"vs previous bill (**{prev.get('month', 'Previous')}**: {prev.get('units', 0.0):.0f} units, {prev.get('days', 30)} days)."
        if lang == "en" else
        f"ಪ್ರಸ್ತುತ ಬಿಲ್ (**{cur.get('month', 'ಇತ್ತೀಚಿನ')}**: {cur.get('units', 0.0):.0f} ಯೂನಿಟ್, {cur.get('days', 30)} ದಿನ) vs "
        f"ಹಿಂದಿನ ಬಿಲ್ (**{prev.get('month', 'ಹಿಂದಿನ')}**: {prev.get('units', 0.0):.0f} ಯೂನಿಟ್, {prev.get('days', 30)} ದಿನ) ಹೋಲಿಕೆ."
    )

st.divider()

# Existing answers for pre-filling
saved = st.session_state.get("answers", {})
if not isinstance(saved, dict):
    saved = {}

# -----------------------------------------------------------------------------
# Render the 9 Household Questions (Directly interactive & fully unlocked)
# -----------------------------------------------------------------------------
st.subheader("🏠 " + ("Household Lifestyle Questions" if lang == "en" else "ಮನೆಯ ಜೀವನಶೈಲಿ ಪ್ರಶ್ನೆಗಳು"))

form_values = {}
col1, col2 = st.columns(2, gap="large")

half = (len(questions.QUESTIONS) + 1) // 2
left_qs = questions.QUESTIONS[:half]
right_qs = questions.QUESTIONS[half:]

def render_question(q, container):
    key = q["key"]
    label = text.T(q["label_key"], lang)
    if label == q["label_key"]:
        label = q["label"]
    help_text = q.get("help", "")

    container.markdown(f"**{label}**")
    if help_text:
        container.caption(help_text)

    if q["type"] == "number":
        cur_val = int(saved.get(key, q.get("default", 0)) or 0)
        form_values[key] = container.number_input(
            label=f"Enter {key}",
            label_visibility="collapsed",
            min_value=q.get("min", 0),
            max_value=q.get("max", 45),
            value=max(cur_val, 0),
            step=1,
            key=f"input_{key}"
        )

    elif q["type"] == "guests_group":
        g_people = int(saved.get("guests_people", 0) or 0)
        g_days = int(saved.get("guests_days", 0) or 0)
        has_guests = container.checkbox(
            "Yes, guests stayed over" if lang == "en" else "ಹೌದು, ಅತಿಥಿಗಳು ಉಳಿದುಕೊಂಡಿದ್ದರು",
            value=(g_people > 0 or bool(saved.get("guests", False))),
            key="chk_guests_toggle"
        )
        if has_guests:
            gc1, gc2 = container.columns(2)
            with gc1:
                p_val = gc1.number_input(
                    "Number of guests" if lang == "en" else "ಅತಿಥಿಗಳ ಸಂಖ್ಯೆ",
                    min_value=1,
                    max_value=25,
                    value=max(g_people, 1),
                    step=1,
                    key="inp_gp"
                )
            with gc2:
                d_val = gc2.number_input(
                    "Days they stayed" if lang == "en" else "ಉಳಿದುಕೊಂಡ ದಿನಗಳು",
                    min_value=1,
                    max_value=45,
                    value=max(g_days, 1),
                    step=1,
                    key="inp_gd"
                )
            form_values["guests"] = True
            form_values["guests_people"] = p_val
            form_values["guests_days"] = d_val
        else:
            form_values["guests"] = False
            form_values["guests_people"] = 0
            form_values["guests_days"] = 0

    elif q["type"] == "yes_no":
        cur_val = bool(saved.get(key, q.get("default", False)))
        form_values[key] = container.checkbox(
            "Yes" if lang == "en" else "ಹೌದು",
            value=cur_val,
            key=f"chk_{key}"
        )

    elif q["type"] == "multiselect":
        cur_items = saved.get(key, q.get("default", []))
        if not isinstance(cur_items, list):
            cur_items = []
        valid_opts = q.get("options", [])
        pre_selected = [it for it in cur_items if it in valid_opts]
        form_values[key] = container.multiselect(
            label="Select appliances",
            label_visibility="collapsed",
            options=valid_opts,
            default=pre_selected,
            placeholder="Select appliances (leave empty if none)" if lang == "en" else "ಸಾಧನಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ",
            key=f"ms_{key}"
        )
    container.markdown("---")

with col1:
    for q in left_qs:
        render_question(q, col1)

with col2:
    for q in right_qs:
        render_question(q, col2)

st.markdown("<br>", unsafe_allow_html=True)
save_btn = st.button(
    "💾 Save and see results →" if lang == "en" else "💾 ಉಳಿಸಿ ಮತ್ತು ಫಲಿತಾಂಶ ನೋಡಿ →",
    type="primary",
    use_container_width=True
)

if save_btn:
    normalized = questions.normalize_answers(form_values)
    st.session_state["answers"] = normalized
    st.session_state["bill_answers"] = normalized

    st.success("✅ " + ("Answers saved! Opening results..." if lang == "en" else "ಉತ್ತರಗಳನ್ನು ಉಳಿಸಲಾಗಿದೆ! ಫಲಿತಾಂಶ ಪುಟ ತೆರೆಯಲಾಗುತ್ತಿದೆ..."))

    try:
        st.switch_page("pages/5_Results.py")
    except Exception:
        try:
            st.page_link("pages/5_Results.py", label="Open Results Page →", icon="📊")
        except Exception:
            st.markdown("[👉 **Open Results Page**](5_Results)")
