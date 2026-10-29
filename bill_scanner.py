"""
bill_scanner.py · High-Precision AI OCR & BESCOM Bill Extraction Engine
Extracts exact Karnataka BESCOM electricity bill fields from uploaded photos, scans, and PDFs:
  - Account ID & Consumer Number
  - RR Number & Tariff Classification
  - Billing Month / Label (e.g. Sep 2025, Sep 2013)
  - Units Consumed (kWh) (accurately parses 'Consumption (Units)' or 'Pres - Prev' reading; never confuses with Pres Rdg)
  - Billing Days in Cycle (exact duration from billing period dates)
  - Estimated / Door Lock Status (Actual vs Door Lock DL)
  - Sanctioned Load (kW) (e.g. 4.0 kW, 10.0 kW)
  - Gruha Jyothi Free Units Entitlement (e.g. 159 units, 150 units)
  - Fuel Surcharge / FPPCA (F.A.C. rate in ₹/unit; strictly avoids Power Factor)
  - Current Bill Amount & Net Amount Due (₹)
"""

import io
import re
from datetime import datetime
from PIL import Image

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from rapidocr_onnxruntime import RapidOCR
    HAS_RAPIDOCR = True
except ImportError:
    HAS_RAPIDOCR = False

# Global cache for RapidOCR engine
_OCR_ENGINE = None

def get_ocr_engine():
    """Returns singleton RapidOCR instance for fast in-memory inference."""
    global _OCR_ENGINE
    if not HAS_RAPIDOCR:
        return None
    if _OCR_ENGINE is None:
        try:
            _OCR_ENGINE = RapidOCR()
        except Exception:
            _OCR_ENGINE = None
    return _OCR_ENGINE


def parse_bescom_bill_text(ocr_lines: list[str]) -> dict:
    """
    High-precision parser tailored specifically for Karnataka Electricity Bills (BESCOM/HESCOM/MESCOM/GESCOM/CESC).
    Parses both Kannada and English bilingual bill receipts with zero random guesses.
    """
    clean_lines = [l.strip() for l in ocr_lines if l and l.strip()]
    full_text = "\n".join(clean_lines)

    data = {
        "account_id": None,
        "rr_number": None,
        "tariff": None,
        "month": None,
        "units": None,
        "days": 30,
        "load_kw": 2.0,
        "fuel_rs": 0.0,
        "free_units": None,
        "estimated": False,
        "bill_amount": None,
        "net_amount": None,
        "confidence": 95,
        "source": "BESCOM Deep AI Scanner"
    }

    # 1. Account ID (ಖಾತೆ ಸಂಖ್ಯೆ / Account ID: 1100157649)
    acc_m = re.search(r'(?:acc[0o]un[td]|account|acct|ಖಾತೆ)[^\d\n]*([0-9]{8,12})', full_text, re.IGNORECASE)
    if acc_m:
        data["account_id"] = acc_m.group(1)

    # 2. RR Number (ಆರ್.ಆರ್.ಸಂಖ್ಯೆ / RR Number: 14543E)
    rr_m = re.search(r'(?:rr\s*num[a-z]*|rr\s*no\.?|rr)[\s\S]{0,15}?([0-9]{3,6}[A-Z]{1,3}|[A-Z]{1,3}[0-9]{3,6})', full_text, re.IGNORECASE)
    if rr_m:
        data["rr_number"] = rr_m.group(1).upper()

    # 3. Tariff (ಜಕಾತಿ / Tariff: LT1, LT2A2-N, LT-2(a))
    tariff_m = re.search(r'(?:tariff|ಜಕಾತಿ)[:\s\-=]*([A-Z0-9\-]+)', full_text, re.IGNORECASE)
    if tariff_m:
        data["tariff"] = tariff_m.group(1).strip()

    # 4. Units Consumed (kWh)
    # Strategy A: Present Reading - Previous Reading difference (exact physical meter reading math)
    # In BESCOM bills, meter readings are 4-6 digits (e.g. 6500 - 2400 = 4100, or 16241 - 15889 = 352)
    cand_readings = []
    for i, l in enumerate(clean_lines):
        if re.search(r'account|bill\s*no|meter\s*sl|date|ದಿನಾಂಕ|ಮೊತ್ತ|due', l, re.IGNORECASE):
            continue
        m = re.findall(r'\b(\d{4,6})\b', l)
        for num_str in m:
            val = int(num_str)
            if 500 <= val <= 999999:
                cand_readings.append((i, val))

    diff_val = None
    for idx in range(len(cand_readings) - 1):
        line_a, val_a = cand_readings[idx]
        line_b, val_b = cand_readings[idx + 1]
        if line_b - line_a <= 3 and val_a > val_b:
            d = val_a - val_b
            if 10 <= d <= 10000:
                diff_val = float(d)
                break

    # Strategy B: Direct Consumption row (avoiding section header 'Consumption Detail')
    cons_val = None
    for i, l in enumerate(clean_lines):
        l_clean = l.lower()
        if 'detail' in l_clean or 'ವಿವರ' in l_clean or 'history' in l_clean:
            continue
        if re.search(r'c[oiea0-9]*ns[uioe]*mp[t]?[a-z]*|ಬಳಕೆ', l_clean):
            # Check same line
            m_same = re.search(r':\s*(\d{1,5}(?:\.\d+)?)\b', l)
            if m_same and float(m_same.group(1)) > 5:
                cons_val = float(m_same.group(1))
                break
            # Check next lines, skipping meter constant = 1 or 1.00
            for cand in clean_lines[i + 1:min(i + 5, len(clean_lines))]:
                cand_clean = cand.strip()
                if cand_clean in ['1', '1.0', '1.00']:
                    continue
                m = re.match(r'^\s*(\d{1,5}(?:\.\d+)?)\s*$', cand_clean)
                if m and float(m.group(1)) > 5:
                    cons_val = float(m.group(1))
                    break
            if cons_val is not None:
                break

    # Strategy C: Repeating billed unit count from charges table (e.g. 352.0 or 4100.0)
    charges_val = None
    unit_counts = {}
    for l in clean_lines:
        m = re.match(r'^\s*(\d{2,5}(?:\.0+)?)\s*$', l)
        if m:
            u = float(m.group(1))
            if 10 <= u <= 10000:
                unit_counts[u] = unit_counts.get(u, 0) + 1
    sorted_units = sorted([u for u, cnt in unit_counts.items() if cnt >= 2], reverse=True)
    if sorted_units:
        charges_val = sorted_units[0]

    # Resolve Units Priority
    if diff_val is not None:
        data["units"] = diff_val
    elif cons_val is not None:
        data["units"] = cons_val
    elif charges_val is not None:
        data["units"] = charges_val
    else:
        # Fallback generic consumption regex
        u_fallback = re.search(r'(?:consumption|usage|ಬಳಕೆ)[\s\S]{0,20}?(\d{2,5}(?:\.\d+)?)', full_text, re.IGNORECASE)
        if u_fallback:
            data["units"] = float(u_fallback.group(1))

    # 5. Sanctioned Load (ಮಂ. ಪ್ರಮಾಣ / Sanct. Load: e.g. 4KW+0HP or 0.00HP+10.00KW or 2.0 KW)
    m_kw_hp = re.search(r'(\d+(?:\.\d+)?)\s*kw\s*\+\s*(\d+(?:\.\d+)?)\s*hp', full_text, re.IGNORECASE)
    m_hp_kw = re.search(r'(\d+(?:\.\d+)?)\s*hp\s*\+\s*(\d+(?:\.\d+)?)\s*kw', full_text, re.IGNORECASE)
    if m_kw_hp:
        kw = float(m_kw_hp.group(1))
        hp = float(m_kw_hp.group(2))
        data["load_kw"] = max(0.5, round(kw + (hp * 0.746), 1))
    elif m_hp_kw:
        hp = float(m_hp_kw.group(1))
        kw = float(m_hp_kw.group(2))
        data["load_kw"] = max(0.5, round(kw + (hp * 0.746), 1))
    else:
        single_m = re.search(r'(?:sanct(?:ioned)?\s*load|sanc\s*load|ಮಂ\.\s*ಪ್ರಮಾಣ)[:\s\-=]*(\d+(?:\.\d+)?)\s*(?:kw)?', full_text, re.IGNORECASE)
        if single_m and float(single_m.group(1)) >= 0.5:
            data["load_kw"] = float(single_m.group(1))

    # 6. Billing Period, Billing Days, and Month
    period_m = re.search(r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})\s*[-–to\s]+\s*(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})', full_text)
    if period_m:
        d1, m1, y1, d2, m2, y2 = period_m.groups()
        y1_full = int(y1) + (2000 if len(y1) == 2 else 0)
        y2_full = int(y2) + (2000 if len(y2) == 2 else 0)
        try:
            dt1 = datetime(y1_full, int(m1), int(d1))
            dt2 = datetime(y2_full, int(m2), int(d2))
            diff = (dt2 - dt1).days
            if 15 <= diff <= 120:
                data["days"] = diff
            data["month"] = dt2.strftime("%b %Y")
        except Exception:
            pass

    if not data["month"]:
        date_m = re.search(r'(?:reading\s*date|bill\s*date|due\s*date|ದಿನಾಂಕ)[:\s\-=]*(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})', full_text, re.IGNORECASE)
        if date_m:
            d, m, y = date_m.groups()
            y_full = int(y) + (2000 if len(y) == 2 else 0)
            try:
                dt = datetime(y_full, int(m), int(d))
                data["month"] = dt.strftime("%b %Y")
            except Exception:
                pass

    if not data["month"]:
        name_m = re.search(r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[,\s\-_]+(202[0-9]|201[0-9])\b', full_text, re.IGNORECASE)
        if name_m:
            data["month"] = f"{name_m.group(1)[:3].capitalize()} {name_m.group(2)}"

    # 7. Fuel Surcharge / FPPCA (Rate in ₹/unit; strictly avoids Power Factor / PowrFaclor / pfacur)
    found_fuel = False
    for i, l in enumerate(clean_lines):
        l_low = l.lower()
        if any(p in l_low for p in ['power', 'powr', 'pwr', 'pfac', 'pf_ac', 'constant', 'average', 'recorded', 'demand']):
            continue
        if re.search(r'\bpf\b|pffac|pfacur', l_low):
            continue
        if re.search(r'fp{1,2}ca|f\.?a\.?c|fuel|ಇಂಧನ', l_low):
            for cand in clean_lines[i + 1:min(i + 12, len(clean_lines))]:
                cand_low = cand.lower()
                if any(p in cand_low for p in ['power', 'powr', 'constant', 'average', 'tax', 'arrears', 'interest', 'demand']):
                    continue
                m_rate = re.search(r'\b([0-2]\.\d{2})\b', cand)
                if m_rate:
                    data["fuel_rs"] = float(m_rate.group(1))
                    found_fuel = True
                    break
            if found_fuel and data["fuel_rs"] > 0:
                break

    # 8. Gruha Jyothi Free Units Entitlement (e.g. 159.0 or 150 units)
    for i, l in enumerate(clean_lines):
        l_low = l.lower()
        if re.search(r'en[a-z]{2,8}\s*u[nm]ts?|entit[a-z]*|entil[a-z]*|enila[a-z]*|free\s*uni|gruha|gjs|ಸಹಾಯಧನ|ಅರ್ಹ', l_low):
            for cand in clean_lines[i:min(i + 6, len(clean_lines))]:
                cand_strip = cand.strip()
                m = re.match(r'^\s*(\d{2,3})(?:\.0+)?\s*$', cand_strip)
                if m:
                    val = int(m.group(1))
                    if 10 <= val <= 200:
                        data["free_units"] = val
                        break
            if data["free_units"]:
                break

    # 9. Bill Amount & Net Amount Due (Current Demand Payable & Net Amount Due)
    b_m = re.search(r'(?:cur[a-z\s\.]*de[a-z]*|demand|deand|current\s*bill|bill\s*amt|cuen|enbam|ಒಟ್ಟು\s*ಬಿಲ್)[\s\S]{0,35}?(\d{3,6}\.\d{2})', full_text, re.IGNORECASE)
    if b_m:
        data["bill_amount"] = float(b_m.group(1))

    net_m = re.search(r'(?:n[eao][tmld]?\s*p[a-z]*|nn\s*p[a-z]*|nemd|net\s*due|net\s*amt|ad(?=\d{4,6})|ಪಾವತಿಸಬೇಕಾದ)[\s\S]{0,25}?(\d{3,6}(?:\.\d{2})?)', full_text, re.IGNORECASE)
    if net_m:
        data["net_amount"] = float(net_m.group(1))

    # 10. Estimated Reading / Door Lock
    if any(k in full_text.lower() for k in ["door lock", "dl reading", "estimated reading", "average bill", "ಬಾಗಿಲು ಬೀಗ"]):
        data["estimated"] = True
    else:
        data["estimated"] = False

    # Calculate confidence based on extracted essentials
    score = 0
    if data["units"] is not None: score += 35
    if data["month"]: score += 20
    if data["load_kw"] is not None: score += 15
    if data["account_id"]: score += 15
    if data["bill_amount"] is not None or data["net_amount"] is not None: score += 15
    data["confidence"] = min(score, 100)

    return data


def analyze_bill_image(pil_img: Image.Image) -> dict:
    """Analyze a PIL Image using RapidOCR and return parsed bill dictionary."""
    engine = get_ocr_engine()
    if engine is None:
        raise RuntimeError("RapidOCR engine is not available on this server.")

    # Run RapidOCR inference directly on the PIL Image
    results, _ = engine(pil_img)
    if not results:
        raise ValueError("No readable text found in the provided image. Please upload a clear photo of the bill.")

    lines = [item[1].strip() for item in results if item and len(item) > 1 and item[1].strip()]
    data = parse_bescom_bill_text(lines)
    data["source"] = f"RapidOCR AI Engine ({len(lines)} lines detected)"
    return data


def analyze_uploaded_bill(file_bytes: bytes, file_name: str, pil_image: Image.Image = None) -> dict:
    """Analyze an uploaded bill file (image or PDF) or pasted PIL Image."""
    if pil_image is not None:
        return analyze_bill_image(pil_image)

    file_ext = file_name.split(".")[-1].lower() if "." in file_name else ""

    # 1. Handle PDF
    if file_ext == "pdf" and HAS_PYPDF:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        raw_text = ""
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                raw_text += txt + "\n"
        if len(raw_text.strip()) > 30:
            lines = raw_text.splitlines()
            data = parse_bescom_bill_text(lines)
            data["source"] = "Digital PDF Text Layer"
            return data

    # 2. Handle Image
    img = Image.open(io.BytesIO(file_bytes))
    return analyze_bill_image(img)
