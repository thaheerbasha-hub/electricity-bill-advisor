"""
3_My_Bills.py · Manage Monthly Electricity Bills
Assigned to: THAHEER
Features:
  - Smart Bill Scanner: Upload electricity bill photo / PDF or try sample bills
  - AI & Rule-based Bill Analyzer: Auto-extracts month, units, days, load, fuel, free units
  - Auto-fill capability for the bill entry form
  - Full manual entry & editing support retained
  - Historical bills table & bill deletion
  - Fully bilingual (English / Kannada)
"""

import io
import streamlit as st
import pandas as pd
from PIL import Image
import db
import ui_common
import text
import bill_scanner

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

    # 1. OPTIONAL: SMART BILL SCANNER & AUTO-FILL
    st.markdown("### 📸 " + ("Scan & Auto-Fill from Bill Image / PDF" if lang == "en" else "ಬಿಲ್ ಫೋಟೋ / PDF ಸ್ಕ್ಯಾನ್ ಮಾಡಿ (AI ಸ್ವಯಂ-ತುಂಬುವಿಕೆ)"))
    st.caption("Upload a photo or PDF of your BESCOM bill — our scanner will read your units, days, and fuel charges automatically, or you can fill the form manually below." if lang == "en" else "ನಿಮ್ಮ ಬೆಸ್ಕಾಂ ಬಿಲ್ ಫೋಟೋ ಅಥವಾ PDF ಅಪ್ಲೋಡ್ ಮಾಡಿ — ನಮ್ಮ ಸ್ಕ್ಯಾನರ್ ನಿಮ್ಮ ಯೂನಿಟ್‌ಗಳು ಮತ್ತು ಶುಲ್ಕಗಳನ್ನು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಗುರುತಿಸುತ್ತದೆ.")

    scan_col1, scan_col2 = st.columns([1, 1])

    with scan_col1:
        uploaded_file = st.file_uploader(
            "Upload Bill Photo or PDF" if lang == "en" else "ಬಿಲ್ ಫೋಟೋ ಅಥವಾ PDF ಅಪ್ಲೋಡ್ ಮಾಡಿ",
            type=["png", "jpg", "jpeg", "webp", "pdf"],
            key="bill_file_uploader",
            help="Supports clear photos of BESCOM bills, digital e-bills, or PDFs."
        )

    with scan_col2:
        sample_choice = st.selectbox(
            "Or try a sample Karnataka BESCOM bill:" if lang == "en" else "ಅಥವಾ ಮಾದರಿ ಕರ್ನಾಟಕ ಬೆಸ್ಕಾಂ ಬಿಲ್ ಪರೀಕ್ಷಿಸಿ:",
            options=["None"] + list(bill_scanner.SAMPLE_BILLS.keys()),
            format_func=lambda k: ("— Select a sample bill to test —" if lang == "en" else "— ಪರೀಕ್ಷಿಸಲು ಮಾದರಿ ಬಿಲ್ ಆಯ್ಕೆಮಾಡಿ —") if k == "None" else bill_scanner.SAMPLE_BILLS[k]["title"],
            key="sample_bill_picker"
        )

    # Process scanned/chosen bill if present
    extracted_data = None
    preview_img = None

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        extracted_data = bill_scanner.analyze_uploaded_bill(file_bytes, uploaded_file.name)
        if uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            try:
                preview_img = Image.open(io.BytesIO(file_bytes))
            except Exception:
                preview_img = None
    elif sample_choice != "None":
        s_data = bill_scanner.SAMPLE_BILLS[sample_choice]
        extracted_data = {
            "month": s_data["month"],
            "units": s_data["units"],
            "days": s_data["days"],
            "estimated": s_data["estimated"],
            "load_kw": s_data["load_kw"],
            "free_units": s_data["free_units"],
            "fuel_rs": s_data["fuel_rs"],
            "confidence": 95,
            "source": "BESCOM Digital Sample Bill"
        }
        preview_img = bill_scanner.generate_bill_preview_image(s_data)

    # If extraction succeeded, show review card and Auto-fill button
    if extracted_data:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### ✅ " + ("Bill Analysis Successful" if lang == "en" else "ಬಿಲ್ ವಿಶ್ಲೇಷಣೆ ಯಶಸ್ವಿಯಾಗಿದೆ"))

            rev_col1, rev_col2 = st.columns([1, 1])
            with rev_col1:
                if preview_img:
                    st.image(preview_img, caption="Detected Bill Scan / Preview", use_container_width=True)
                else:
                    st.info(f"📄 Scanned Document: **{uploaded_file.name if uploaded_file else 'Digital Bill'}**")

            with rev_col2:
                st.markdown("**" + ("Extracted Parameters:" if lang == "en" else "ಗುರುತಿಸಲಾದ ವಿವರಗಳು:") + "**")
                st.write(f"• **Billing Month:** `{extracted_data.get('month', 'N/A')}`")
                st.write(f"• **Units Consumed:** `{extracted_data.get('units', 0.0):.1f} kWh`")
                st.write(f"• **Billing Days in Cycle:** `{extracted_data.get('days', 30)} days`")
                st.write(f"• **Sanctioned Load:** `{extracted_data.get('load_kw', 2.0):.1f} kW`")
                st.write(f"• **Gruha Jyothi Free Units:** `{extracted_data.get('free_units', 'N/A')} units`")
                st.write(f"• **Fuel Surcharge (FPPCA):** `₹{extracted_data.get('fuel_rs', 0.37):.2f} / unit`")
                st.write(f"• **Reading Type:** `{'Estimated (Door Lock) ⚠️' if extracted_data.get('estimated') else 'Actual Reading ✅'}`")

                if st.button("✨ " + ("Auto-Fill Form Below" if lang == "en" else "ಕೆಳಗಿನ ಫಾರ್ಮ್‌ಗೆ ತುಂಬಿರಿ"), type="primary", use_container_width=True):
                    st.session_state["bill_prefill"] = extracted_data
                    st.session_state["prefill_counter"] = st.session_state.get("prefill_counter", 0) + 1
                    st.rerun()

    st.divider()

    # 2. MANUAL BILL ENTRY FORM (Pre-filled if auto-fill used, or editable from scratch)
    prefill = st.session_state.get("bill_prefill", {})

    st.markdown("### ✍️ " + ("Bill Form (Manual / Auto-Filled)" if lang == "en" else "ಬಿಲ್ ನಮೂದು ಫಾರ್ಮ್ (ಹಸ್ತಚಾಲಿತ / ಸ್ವಯಂ-ತುಂಬಿದ)"))
    st.caption("You can freely edit, verify, or type any value below before saving." if lang == "en" else "ಉಳಿಸುವ ಮೊದಲು ನೀವು ಕೆಳಗಿನ ಯಾವುದೇ ಮೌಲ್ಯವನ್ನು ತಿದ್ದುಪಡಿ ಮಾಡಬಹುದು ಅಥವಾ ಹೊಸದಾಗಿ ನಮೂದಿಸಬಹುದು.")

    def_month = prefill.get("month", "") or "Nov 2026"
    def_units = float(prefill.get("units", 170.0))
    def_days = int(prefill.get("days", 30))
    def_est = bool(prefill.get("estimated", False))
    def_kw = float(prefill.get("load_kw", 2.0))
    def_gj = (prefill.get("free_units") is not None) if "free_units" in prefill else True
    def_free = int(prefill.get("free_units", 150) or 150)
    def_fuel = float(prefill.get("fuel_rs", 0.37))

    k_prefix = f"pf_{st.session_state.get('prefill_counter', 0)}"

    with st.form("add_bill_form"):
        c1, c2 = st.columns(2)
        with c1:
            month = st.text_input(
                text.T("bill_month_label", lang),
                value=def_month,
                placeholder="e.g. Nov 2026",
                key=f"{k_prefix}_month"
            )
            units = st.number_input(
                text.T("bill_units_label", lang),
                min_value=0.0,
                max_value=5000.0,
                value=def_units,
                step=1.0,
                key=f"{k_prefix}_units"
            )
            days = st.number_input(
                text.T("bill_days_label", lang),
                min_value=15,
                max_value=60,
                value=def_days,
                step=1,
                key=f"{k_prefix}_days"
            )
            estimated = st.checkbox(
                text.T("bill_est_label", lang),
                value=def_est,
                key=f"{k_prefix}_est"
            )
        with c2:
            load_kw = st.number_input(
                text.T("bill_kw_label", lang),
                min_value=0.5,
                max_value=25.0,
                value=def_kw,
                step=0.5,
                key=f"{k_prefix}_kw"
            )
            in_gj = st.checkbox(
                text.T("bill_gj_enrolled", lang),
                value=def_gj,
                key=f"{k_prefix}_gj"
            )
            free_units = st.number_input(
                text.T("bill_free_label", lang),
                min_value=0,
                max_value=200,
                value=def_free,
                step=1,
                key=f"{k_prefix}_free"
            ) if in_gj else None
            fuel_rs = st.number_input(
                text.T("bill_fuel_label", lang),
                min_value=0.0,
                max_value=5.0,
                value=def_fuel,
                step=0.01,
                key=f"{k_prefix}_fuel"
            )

        submitted = st.form_submit_button(text.T("bill_save_btn", lang), type="primary", use_container_width=True)
        if submitted:
            if not month.strip():
                st.error("Please enter a month label." if lang == "en" else "ದಯವಿಟ್ಟು ತಿಂಗಳ ಹೆಸರು ನಮೂದಿಸಿ.")
            else:
                db.add_bill(user["id"], month.strip(), units, days, estimated, fuel_rs, free_units, load_kw)
                if "bill_prefill" in st.session_state:
                    del st.session_state["bill_prefill"]
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
        del_id = st.selectbox(
            "Select Bill to Delete" if lang == "en" else "ಅಳಿಸಲು ಬಿಲ್ ಆಯ್ಕೆಮಾಡಿ",
            options=[b["id"] for b in bills],
            format_func=lambda i: next(f"ID {b['id']} - {b['month']} ({b['units']} units)" for b in bills if b["id"] == i)
        )
        if st.button(text.T("bills_del_btn", lang), type="secondary"):
            db.delete_bill(del_id, user["id"])
            st.success("Bill deleted." if lang == "en" else "ಬಿಲ್ ಅಳಿಸಲಾಗಿದೆ.")
            st.rerun()
else:
    st.info("No bills saved yet. Fill out the form above to record your first bill!" if lang == "en" else "ಇನ್ನೂ ಯಾವುದೇ ಬಿಲ್‌ಗಳು ದಾಖಲಾಗಿಲ್ಲ. ಮೇಲೆ ನೀಡಿರುವ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಿ!")
