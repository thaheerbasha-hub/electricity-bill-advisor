"""
3_My_Bills.py · Manage Monthly Electricity Bills
Assigned to: THAHEER
Features:
  - Smart Bill Scanner: Drag-and-drop file upload (PNG, JPG, PDF) or copy-paste directly from clipboard (Ctrl+V)
  - Rapid AI OCR Engine: Automatically and accurately extracts exact Karnataka BESCOM bill parameters in seconds
  - Auto-fills Month, Units, Billing Days, Sanctioned Load, Fuel Surcharge, and Subsidy Status
  - 100% Manual entry & editing support retained
  - Saved bills table with daily average calculations & bill deletion
  - Fully bilingual (English / Kannada)
"""

import io
import importlib
import streamlit as st
import pandas as pd
from PIL import Image
import db
import ui_common
import text
import bill_scanner

# Ensure fresh reload of bill_scanner module
importlib.reload(bill_scanner)

try:
    from streamlit_paste_button import paste_image_button
    HAS_PASTE_BTN = True
except ImportError:
    HAS_PASTE_BTN = False

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

    # 1. SMART BILL SCANNER (DRAG-AND-DROP OR CLIPBOARD COPY-PASTE)
    st.markdown("### 📸 " + ("Scan & Auto-Fill from Bill Image / PDF" if lang == "en" else "ಬಿಲ್ ಫೋಟೋ / PDF ಸ್ಕ್ಯಾನ್ ಮಾಡಿ (AI ಸ್ವಯಂ-ತುಂಬುವಿಕೆ)"))
    st.caption(
        "Upload a photo/PDF or paste a copied bill screenshot (Ctrl+V) — our AI scanner accurately extracts units, billing cycle, sanctioned load, and fuel charges automatically in seconds."
        if lang == "en" else
        "ಬಿಲ್ ಫೋಟೋ/PDF ಅಪ್ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕಾಪಿ ಮಾಡಿದ ಚಿತ್ರವನ್ನು ಪೇಸ್ಟ್ ಮಾಡಿ — ನಮ್ಮ AI ಸ್ಕ್ಯಾನರ್ ನಿಮ್ಮ ಯೂನಿಟ್‌ಗಳು, ದಿನಗಳು ಮತ್ತು ಶುಲ್ಕಗಳನ್ನು ಕ್ಷಣಾರ್ಧದಲ್ಲಿ ಗುರುತಿಸುತ್ತದೆ."
    )

    scan_col1, scan_col2 = st.columns([1.2, 0.8])

    with scan_col1:
        uploaded_file = st.file_uploader(
            "📂 " + ("Drag & Drop Bill Photo or PDF" if lang == "en" else "ಬಿಲ್ ಫೋಟೋ ಅಥವಾ PDF ಡ್ರ್ಯಾಗ್ & ಡ್ರಾಪ್ ಮಾಡಿ"),
            type=["png", "jpg", "jpeg", "webp", "pdf"],
            key="bill_file_uploader",
            help="Drag and drop or browse clear photos of BESCOM bills, digital e-bills, or PDFs."
        )

    with scan_col2:
        st.markdown("**" + ("📋 Or Paste from Clipboard:" if lang == "en" else "📋 ಅಥವಾ ಕ್ಲಿಪ್‌ಬೋರ್ಡ್‌ನಿಂದ ಪೇಸ್ಟ್ ಮಾಡಿ:") + "**")
        paste_result = None
        if HAS_PASTE_BTN:
            paste_result = paste_image_button(
                label="📋 " + ("Paste Copied Bill Image" if lang == "en" else "ಕಾಪಿ ಮಾಡಿದ ಬಿಲ್ ಚಿತ್ರ ಪೇಸ್ಟ್ ಮಾಡಿ"),
                text_color="#ffffff",
                background_color="#059669",
                hover_background_color="#047857",
                key="bill_clipboard_paste"
            )
            st.caption(
                "💡 *Copy any screenshot (Win+Shift+S / Snipping Tool / Ctrl+C), then click the Paste button.*"
                if lang == "en" else
                "💡 *ಯಾವುದೇ ಬಿಲ್ ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಕಾಪಿ ಮಾಡಿ, ನಂತರ ಮೇಲಿನ ಪೇಸ್ಟ್ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.*"
            )
        else:
            st.info("Direct clipboard paste requires streamlit-paste-button package.")

    # Process scanned bill (from Drag & Drop or Clipboard Paste)
    extracted_data = None
    preview_img = None
    doc_source = None
    scan_error = None

    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)
            file_bytes = uploaded_file.read()
            uploaded_file.seek(0)
            doc_source = uploaded_file.name
            
            # Cache key to prevent re-running OCR repeatedly on every widget interaction
            cache_key = f"scan_{uploaded_file.name}_{len(file_bytes)}"
            if st.session_state.get("active_scan_key") == cache_key and "active_scan_data" in st.session_state:
                extracted_data = st.session_state["active_scan_data"]
                preview_img = st.session_state.get("active_scan_preview")
            else:
                if uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    try:
                        preview_img = Image.open(io.BytesIO(file_bytes))
                    except Exception:
                        preview_img = None

                with st.spinner("⚡ " + ("Analyzing bill layout with AI Vision Scanner..." if lang == "en" else "AI ಸ್ಕ್ಯಾನರ್ ಮೂಲಕ ಬಿಲ್ ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...")):
                    extracted_data = bill_scanner.analyze_uploaded_bill(file_bytes, uploaded_file.name, pil_image=preview_img)
                    st.session_state["active_scan_key"] = cache_key
                    st.session_state["active_scan_data"] = extracted_data
                    st.session_state["active_scan_preview"] = preview_img
        except Exception as ex:
            scan_error = str(ex)

    elif paste_result and paste_result.image_data is not None:
        try:
            preview_img = paste_result.image_data
            doc_source = "Clipboard Pasted Image"
            with st.spinner("⚡ " + ("Analyzing pasted bill with AI Vision Scanner..." if lang == "en" else "ಪೇಸ್ಟ್ ಮಾಡಿದ ಬಿಲ್ ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...")):
                extracted_data = bill_scanner.analyze_bill_image(preview_img)
        except Exception as ex:
            scan_error = str(ex)

    if scan_error:
        st.error(f"❌ Error scanning bill: {scan_error}. Please ensure the bill image is clear and try again.")

    # If extraction succeeded, show review card and Auto-fill button
    if extracted_data:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                "#### ✅ " + ("Bill Analysis Successful" if lang == "en" else "ಬಿಲ್ ವಿಶ್ಲೇಷಣೆ ಯಶಸ್ವಿಯಾಗಿದೆ") +
                f" &nbsp; `<span style='font-size:0.85rem;color:#059669;'>Confidence: {extracted_data.get('confidence', 95)}%</span>`",
                unsafe_allow_html=True
            )

            rev_col1, rev_col2 = st.columns([1, 1.2])
            with rev_col1:
                if preview_img:
                    st.image(preview_img, caption=f"Scanned: {doc_source}", use_container_width=True)
                else:
                    st.info(f"📄 Scanned Document: **{doc_source}**")

            with rev_col2:
                st.markdown("**" + ("Extracted BESCOM Bill Parameters:" if lang == "en" else "ಗುರುತಿಸಲಾದ ಬೆಸ್ಕಾಂ ಬಿಲ್ ವಿವರಗಳು:") + "**")

                # Show Account ID & RR Number if recognized
                id_info = []
                if extracted_data.get("account_id"):
                    id_info.append(f"Account ID: `{extracted_data['account_id']}`")
                if extracted_data.get("rr_number"):
                    id_info.append(f"RR No: `{extracted_data['rr_number']}`")
                if extracted_data.get("tariff"):
                    id_info.append(f"Tariff: `{extracted_data['tariff']}`")
                if id_info:
                    st.write("• **Consumer Info:** " + " · ".join(id_info))

                st.write(f"• **Billing Month:** `{extracted_data.get('month', 'N/A')}`")
                st.write(f"• **Units Consumed:** `{extracted_data.get('units', 0.0):.1f} kWh`")
                st.write(f"• **Billing Days in Cycle:** `{extracted_data.get('days', 30)} days`")
                st.write(f"• **Sanctioned Load:** `{extracted_data.get('load_kw', 2.0):.1f} kW`")

                free_u = extracted_data.get("free_units")
                st.write(f"• **Gruha Jyothi Subsidy:** `{str(free_u) + ' Free Units' if free_u is not None else 'Not Subsidized / ₹0 Subsidy'}`")
                st.write(f"• **Fuel Surcharge (F.A.C.):** `₹{extracted_data.get('fuel_rs', 0.00):.2f} / unit`")
                st.write(f"• **Reading Type:** `{'Estimated (Door Lock) ⚠️' if extracted_data.get('estimated') else 'Actual Reading ✅'}`")

                if extracted_data.get("bill_amount"):
                    st.write(f"• **Current Bill Amount:** `₹{extracted_data['bill_amount']:,.2f}`" + (f" (Net Due: `₹{extracted_data['net_amount']:,.2f}`)" if extracted_data.get("net_amount") else ""))

                st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
                if st.button("✨ " + ("Auto-Fill Form Below" if lang == "en" else "ಕೆಳಗಿನ ಫಾರ್ಮ್‌ಗೆ ತುಂಬಿರಿ"), type="primary", use_container_width=True):
                    st.session_state["bill_prefill"] = extracted_data
                    st.session_state["prefill_counter"] = st.session_state.get("prefill_counter", 0) + 1
                    st.toast("✅ Scanned data applied to bill form below!", icon="⚡")
                    st.rerun()

    st.divider()

    # 2. MANUAL BILL ENTRY FORM (Pre-filled if auto-fill used, or freely editable from scratch)
    prefill = st.session_state.get("bill_prefill", {})

    st.markdown("### ✍️ " + ("Bill Form (Manual / Auto-Filled)" if lang == "en" else "ಬಿಲ್ ನಮೂದು ಫಾರ್ಮ್ (ಹಸ್ತಚಾಲಿತ / ಸ್ವಯಂ-ತುಂಬಿದ)"))
    st.caption("You can freely edit, verify, or type any value below before saving." if lang == "en" else "ಉಳಿಸುವ ಮೊದಲು ನೀವು ಕೆಳಗಿನ ಯಾವುದೇ ಮೌಲ್ಯವನ್ನು ತಿದ್ದುಪಡಿ ಮಾಡಬಹುದು ಅಥವಾ ಹೊಸದಾಗಿ ನಮೂದಿಸಬಹುದು.")

    def_month = prefill.get("month", "") or "Nov 2026"
    def_units = float(prefill.get("units", 170.0))
    def_days = int(prefill.get("days", 30))
    def_est = bool(prefill.get("estimated", False))
    def_kw = float(prefill.get("load_kw", 2.0))
    def_gj = (prefill.get("free_units") is not None) if "free_units" in prefill else False
    def_free = int(prefill.get("free_units", 150) or 150)
    def_fuel = float(prefill.get("fuel_rs", 0.00))

    k_prefix = f"pf_{st.session_state.get('prefill_counter', 0)}"

    with st.form("add_bill_form"):
        c1, c2 = st.columns(2)
        with c1:
            month = st.text_input(
                text.T("bill_month_label", lang),
                value=def_month,
                placeholder="e.g. Sep 2013 or Nov 2026",
                key=f"{k_prefix}_month"
            )
            units = st.number_input(
                text.T("bill_units_label", lang),
                min_value=0.0,
                max_value=50000.0,
                value=def_units,
                step=1.0,
                key=f"{k_prefix}_units"
            )
            days = st.number_input(
                text.T("bill_days_label", lang),
                min_value=15,
                max_value=120,
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
                max_value=100.0,
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
                max_value=10.0,
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
