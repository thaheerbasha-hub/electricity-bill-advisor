"""
Power Bill Coach · Engine (pure Python, NO streamlit import)
"""

import math

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
RATE = 5.80          # Rs per unit, BESCOM domestic, flat
FIXED_PER_KW = 150   # Rs per kW per month
TAX = 0.09           # tax on the energy charge
GJ_CAP = 200         # Gruha Jyothi: above 200 units the full bill is payable
AWAY_SHARE = 0.30
POWERCUT_SHARE = 0.10

EXTRA_PER_DAY = {
    "guests": 1.2,
    "heat": 3.0,
    "geyser": 1.0,
    "home_more": 1.5,
    "pump": 0.4,
    "festival": 1.5,
    "new_ac": 3.0,
    "new_geyser": 1.0,
    "new_fridge": 1.0,
    "new_washer": 0.3,
    "new_ev": 2.0,
    "new_other": 0.8,
}

NEW_ITEMS = {
    "AC": "new_ac",
    "Geyser": "new_geyser",
    "Fridge": "new_fridge",
    "Washing machine": "new_washer",
    "EV": "new_ev",
    "Other": "new_other",
}


# ------------------------------------------------------------------
# Formatters & Bill math
# ------------------------------------------------------------------
def rupees(x):
    n = int(round(x))
    s = str(abs(n))
    if len(s) > 3:
        head, tail, parts = s[:-3], s[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        s = (",".join([head] + parts) if head else ",".join(parts)) + "," + tail
    return ("-" if n < 0 else "") + "₹" + s


def full_bill(units, days, kw, fuel):
    energy = units * RATE
    return energy + kw * FIXED_PER_KW * days / 30 + units * fuel + energy * TAX


def to_pay(units, days, kw, fuel, free_units):
    """What the family actually pays after Gruha Jyothi."""
    full = full_bill(units, days, kw, fuel)
    if free_units is None or units > GJ_CAP:
        return full
    if units <= free_units:
        return 0.0
    extra = units - free_units
    return extra * (RATE * (1 + TAX) + fuel)   # only the extra units, no fixed charge


# ------------------------------------------------------------------
# Reason data structure
# ------------------------------------------------------------------
class Reason(dict):
    """Reason dict that supports both dictionary and attribute access."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# ------------------------------------------------------------------
# Input Cleaners
# ------------------------------------------------------------------
def _to_num(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, str):
        val = val.strip()
        if not val or val.lower() == "nan":
            return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def _to_int(val, default=0):
    if val is None:
        return default
    if isinstance(val, str):
        val = val.strip()
        if not val or val.lower() == "nan":
            return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return max(0, int(round(f)))
    except (ValueError, TypeError):
        return default


def _to_bool(val):
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        s = val.strip().lower()
        if s in ("true", "yes", "1", "y", "t"):
            return True
        if s in ("false", "no", "0", "n", "f", ""):
            return False
    return bool(val)


def _map_new_item(item):
    if item is None:
        return None
    s = str(item).strip()
    if not s:
        return None
    low = s.lower()
    if low in ("none", "no", "null", "false", "0"):
        return None
    if low == "ac" or "air conditioner" in low:
        return "AC"
    if "geyser" in low or "water heater" in low:
        return "Geyser"
    if "fridge" in low or "refrigerator" in low:
        return "Fridge"
    if "wash" in low:
        return "Washing machine"
    if "ev" in low or "scooter" in low:
        return "EV"
    if low in ("other", "something else") or "something else" in low:
        return "Other"
    return "Other"


def normalize_bill(b):
    if not isinstance(b, dict):
        b = {}
    res = dict(b)

    # month
    res["month"] = str(b.get("month", "") or "") if b.get("month") is not None else ""

    # units
    units = max(0.0, _to_num(b.get("units"), 0.0))
    res["units"] = units

    # days (missing/None/''/NaN numbers -> 0, days default 30, days >= 1)
    if "days" not in b or b.get("days") is None or b.get("days") == "":
        days = 30
    else:
        days = _to_int(b.get("days"), 30)
    res["days"] = max(1, days)

    # estimated (bool)
    res["estimated"] = _to_bool(b.get("estimated", False))

    # fuel_per_unit (accept old key fuel_rs as fuel_per_unit)
    fuel_val = b.get("fuel_per_unit")
    if fuel_val is None or fuel_val == "":
        fuel_val = b.get("fuel_rs")
    fuel = max(0.0, _to_num(fuel_val, 0.0))
    if fuel > 5 and units > 0:
        fuel = fuel / units
    res["fuel_per_unit"] = fuel

    # free_units (None or float)
    raw_free = b.get("free_units")
    if raw_free is None or raw_free == "" or str(raw_free).strip().lower() in ("none", "nan"):
        res["free_units"] = None
    else:
        val = _to_num(raw_free, None)
        res["free_units"] = max(0.0, val) if val is not None else None

    # load_kw (default 2.0)
    if "load_kw" not in b or b.get("load_kw") is None or b.get("load_kw") == "":
        load_kw = 2.0
    else:
        load_kw = max(0.0, _to_num(b.get("load_kw"), 2.0))
    res["load_kw"] = load_kw

    return res


def normalize_answers(a):
    if not isinstance(a, dict):
        a = {}

    def _get_alias(aliases):
        for k in aliases:
            if k in a and a[k] is not None and a[k] != "":
                return a[k]
        for k in aliases:
            if k in a:
                return a[k]
        return None

    away_days = _to_int(_get_alias(("away_days", "vacation_days", "days_away", "vacation", "away")), 0)
    prev_away_days = _to_int(_get_alias(("prev_away_days",)), 0)
    guests_people = _to_int(_get_alias(("guests_people", "guests", "people")), 0)
    guests_days = _to_int(_get_alias(("guests_days", "guest_days")), 0)

    heat = _to_bool(_get_alias(("heat", "hot", "ac", "heat_ac")))
    geyser = _to_bool(_get_alias(("geyser", "cold")))
    home_more = _to_bool(_get_alias(("home_more", "home_in_day", "wfh")))
    pump = _to_bool(_get_alias(("pump", "motor")))
    festival = _to_bool(_get_alias(("festival", "festival_lights", "lights")))
    powercut = _to_bool(_get_alias(("powercut", "power_cuts", "powercuts", "inverter")))

    raw_new = _get_alias(("new_items", "new", "bought"))
    new_items = []
    if raw_new is not None:
        if isinstance(raw_new, str):
            raw_list = [x.strip() for x in raw_new.split(",")] if "," in raw_new else [raw_new.strip()]
        elif isinstance(raw_new, (list, tuple, set)):
            raw_list = list(raw_new)
        else:
            raw_list = [raw_new]

        for item in raw_list:
            mapped = _map_new_item(item)
            if mapped and mapped not in new_items:
                new_items.append(mapped)

    return {
        "away_days": away_days,
        "prev_away_days": prev_away_days,
        "guests_people": guests_people,
        "guests_days": guests_days,
        "heat": heat,
        "geyser": geyser,
        "home_more": home_more,
        "pump": pump,
        "festival": festival,
        "powercut": powercut,
        "new_items": new_items,
    }


# ------------------------------------------------------------------
# Historical usage
# ------------------------------------------------------------------
def normal_use(bills):
    """Calculate normal units per day from historical bills."""
    if not bills:
        return 0.0

    try:
        bill_list = list(bills)
    except Exception:
        return 0.0

    cleaned = []
    for b in bill_list:
        try:
            if isinstance(b, dict):
                cleaned.append(normalize_bill(b))
        except Exception:
            continue

    if not cleaned:
        return 0.0

    recent = cleaned[-6:]

    merged = []
    pending_est = []

    for b in recent:
        if b.get("estimated", False):
            pending_est.append(b)
        else:
            u = float(b.get("units") or 0.0) + sum(float(p.get("units") or 0.0) for p in pending_est)
            d = float(b.get("days") or 0.0) + sum(float(p.get("days") or 0.0) for p in pending_est)
            a = float(b.get("away", 0) or 0.0) + sum(float(p.get("away", 0) or 0.0) for p in pending_est)
            merged.append({"units": u, "days": d, "away": a, "estimated": False})
            pending_est = []

    if pending_est:
        if not merged:
            for p in pending_est:
                merged.append({
                    "units": float(p.get("units") or 0.0),
                    "days": float(p.get("days") or 0.0),
                    "away": float(p.get("away", 0) or 0.0),
                    "estimated": True,
                })

    dailies = []
    for b in merged:
        units = float(b.get("units") or 0.0)
        days = float(b.get("days") or 0.0)
        away = float(b.get("away", 0) or 0.0)
        eff = days - away + AWAY_SHARE * away
        divisor = max(eff, 1.0)
        daily = units / divisor if divisor else 0.0
        dailies.append(daily)

    if not dailies:
        return 0.0
    return sum(dailies) / len(dailies)


# ------------------------------------------------------------------
# Explanation core
# ------------------------------------------------------------------
def _get_tag(key):
    if key in ("days", "catchup", "fuel", "powercut"):
        return "not your usage"
    if key == "gj":
        return "scheme rule"
    return "your usage"


def _get_text(key, u, r, dp, dc, prev_fuel, cur_fuel, uc=0.0):
    if key == "days":
        d_diff = int(round(dc - dp))
        more_less = "more" if d_diff >= 0 else "fewer"
        return f"Billing cycle had {abs(d_diff)} {more_less} day(s) ({u:+.1f} units)."
    if key == "catchup":
        return f"Catch-up from previous estimated meter reading ({u:+.1f} units)."
    if key == "vacation":
        return f"Adjustment for days away from home ({u:+.1f} units)."
    if key == "guests":
        return f"Guests stayed over ({u:+.1f} units)."
    if key == "heat":
        return f"Hot weather and cooling ({u:+.1f} units)."
    if key == "geyser":
        return f"Water heater / geyser usage ({u:+.1f} units)."
    if key == "home_more":
        return f"More time spent at home ({u:+.1f} units)."
    if key == "pump":
        return f"Water pump usage ({u:+.1f} units)."
    if key == "festival":
        return f"Festival lighting ({u:+.1f} units)."
    if key == "powercut":
        return f"Power cuts during the month ({u:+.1f} units)."
    if key == "new_ac":
        return f"New air conditioner ({u:+.1f} units)."
    if key == "new_geyser":
        return f"New water heater / geyser ({u:+.1f} units)."
    if key == "new_fridge":
        return f"New refrigerator ({u:+.1f} units)."
    if key == "new_washer":
        return f"New washing machine ({u:+.1f} units)."
    if key == "new_ev":
        return f"New EV charging ({u:+.1f} units)."
    if key == "new_other":
        return f"New appliance ({u:+.1f} units)."
    if key == "unknown":
        x_units = max(1, int(round(abs(u)))) if abs(u) > 0 else 0
        return f"About {x_units} units not explained."
    if key == "less":
        return f"Used less electricity than usual ({u:+.1f} units)."
    if key == "fuel":
        return f"Fuel surcharge changed from ₹{prev_fuel:.2f} to ₹{cur_fuel:.2f} per unit."
    if key == "gj":
        if uc > GJ_CAP:
            return "Over 200 units, whole bill payable."
        return "Gruha Jyothi scheme subsidy adjustment."
    return f"{key.capitalize()}: {u:+.1f} units."


def explain(bills, answers=None):
    if not bills:
        return [], 0.0, 0.0

    try:
        bills = [normalize_bill(b) for b in bills if isinstance(b, dict)]
    except Exception:
        return [], 0.0, 0.0

    answers = normalize_answers(answers)

    if len(bills) < 2:
        return [], 0.0, normal_use(bills)

    prev = bills[-2]
    cur = bills[-1]

    kw = cur.get("load_kw", 2.0) or 2.0
    prev_fuel = prev.get("fuel_per_unit", 0.0) or 0.0
    cur_fuel = cur.get("fuel_per_unit", 0.0) or 0.0
    prev_free = prev.get("free_units")
    cur_free = cur.get("free_units")

    up = float(prev.get("units", 0.0) or 0.0)
    dp = float(prev.get("days", 30) or 30)
    uc = float(cur.get("units", 0.0) or 0.0)
    dc = float(cur.get("days", 30) or 30)

    away_cur = min(float(answers.get("away_days", 0) or 0), dc)
    away_cur = max(0.0, away_cur)
    away_prev = max(0.0, float(answers.get("prev_away_days", 0) or 0))

    prev_est = bool(prev.get("estimated", False))
    base = normal_use(bills) if prev_est else normal_use(bills[:-1])
    if not base or base <= 0:
        base = up / (dp if dp > 0 else 1.0)

    normal = normal_use(bills)

    u_days = up * dc / (dp if dp > 0 else 1.0)
    eff_cur = (dc - away_cur) + AWAY_SHARE * away_cur
    u_vac = base * eff_cur

    steps = [("days", u_days - up)]
    if prev_est:
        u_vac = uc
        steps.append(("catchup", u_vac - u_days))
    elif away_cur != away_prev:
        steps.append(("vacation", u_vac - u_days))
    else:
        u_vac = u_days

    if not prev_est:
        extra = uc - u_vac
        home_days = max(dc - away_cur, 0.0)

        weights = {}
        guests_people = answers.get("guests_people", 0) or 0
        guests_days = answers.get("guests_days", 0) or 0
        if guests_people > 0 and guests_days > 0 and home_days > 0:
            w_guests = EXTRA_PER_DAY["guests"] * guests_people * min(guests_days, home_days)
            if w_guests > 0:
                weights["guests"] = w_guests

        if answers.get("heat") and home_days > 0:
            w_heat = EXTRA_PER_DAY["heat"] * home_days * 0.5
            if w_heat > 0:
                weights["heat"] = w_heat

        if answers.get("geyser") and home_days > 0:
            w_geyser = EXTRA_PER_DAY["geyser"] * home_days * 0.5
            if w_geyser > 0:
                weights["geyser"] = w_geyser

        if answers.get("home_more") and home_days > 0:
            w_home_more = EXTRA_PER_DAY["home_more"] * home_days * 0.6
            if w_home_more > 0:
                weights["home_more"] = w_home_more

        if answers.get("pump") and home_days > 0:
            w_pump = EXTRA_PER_DAY["pump"] * home_days
            if w_pump > 0:
                weights["pump"] = w_pump

        if answers.get("festival") and home_days > 0:
            w_festival = EXTRA_PER_DAY["festival"] * home_days * 0.4
            if w_festival > 0:
                weights["festival"] = w_festival

        if home_days > 0:
            for item in answers.get("new_items") or []:
                key = NEW_ITEMS.get(item, item)
                if key in EXTRA_PER_DAY:
                    w_item = EXTRA_PER_DAY[key] * home_days * 0.7
                    if w_item > 0:
                        weights[key] = w_item

        if extra > 0:
            tot_weight = sum(weights.values())
            if tot_weight <= 0:
                steps.append(("unknown", extra))
            else:
                share = min(1.0, extra / tot_weight)
                allocated = {k: w * share for k, w in weights.items()}
                leftover = extra - sum(allocated.values())
                threshold = max(5.0, 0.05 * uc)
                if leftover > threshold:
                    for k, u in allocated.items():
                        if u > 0:
                            steps.append((k, u))
                    steps.append(("unknown", leftover))
                else:
                    biggest_k = max(weights, key=weights.get)
                    allocated[biggest_k] += leftover
                    for k, u in allocated.items():
                        if u > 0:
                            steps.append((k, u))
        elif extra < 0:
            abs_extra = abs(extra)
            if answers.get("powercut"):
                pc_units = min(abs_extra, POWERCUT_SHARE * up)
                if pc_units > 0:
                    steps.append(("powercut", -pc_units))
                rest = extra - (-pc_units)
                if rest < -1e-6:
                    steps.append(("less", rest))
            else:
                steps.append(("less", extra))

    raw_reasons = []
    run_u = up
    for k, du in steps:
        before = full_bill(run_u, dp if k == "days" else dc, kw, prev_fuel)
        after = full_bill(run_u + du, dc, kw, prev_fuel)
        diff = after - before
        raw_reasons.append(Reason(
            key=k,
            units=du,
            rupees=diff,
            text=_get_text(k, du, diff, dp, dc, prev_fuel, cur_fuel, uc),
            tag=_get_tag(k)
        ))
        run_u += du

    fuel_diff = full_bill(uc, dc, kw, cur_fuel) - full_bill(uc, dc, kw, prev_fuel)
    raw_reasons.append(Reason(
        key="fuel",
        units=0.0,
        rupees=fuel_diff,
        text=_get_text("fuel", 0.0, fuel_diff, dp, dc, prev_fuel, cur_fuel, uc),
        tag=_get_tag("fuel")
    ))

    cur_gj = to_pay(uc, dc, kw, cur_fuel, cur_free) - full_bill(uc, dc, kw, cur_fuel)
    prev_gj = to_pay(up, dp, kw, prev_fuel, prev_free) - full_bill(up, dp, kw, prev_fuel)
    gj_diff = cur_gj - prev_gj
    raw_reasons.append(Reason(
        key="gj",
        units=0.0,
        rupees=gj_diff,
        text=_get_text("gj", 0.0, gj_diff, dp, dc, prev_fuel, cur_fuel, uc),
        tag=_get_tag("gj")
    ))

    total = round(to_pay(uc, dc, kw, cur_fuel, cur_free) - to_pay(up, dp, kw, prev_fuel, prev_free), 2)

    if all(abs(r["rupees"]) < 1.0 for r in raw_reasons) and abs(total) < 1.0:
        return [], total, normal

    largest = max(raw_reasons, key=lambda r: abs(r["rupees"]))
    kept = []
    folded_rupees = 0.0
    for r in raw_reasons:
        if r is largest:
            continue
        if abs(r["rupees"]) < 1.0:
            folded_rupees += r["rupees"]
        else:
            kept.append(r)

    largest["rupees"] += folded_rupees
    kept.append(largest)

    for r in kept:
        r["rupees"] = round(r["rupees"], 2)
        r["units"] = round(r["units"], 2)

    residue = round(total - sum(r["rupees"] for r in kept), 2)
    largest["rupees"] = round(largest["rupees"] + residue, 2)

    kept.sort(key=lambda r: abs(r["rupees"]), reverse=True)
    return kept, total, normal


# ------------------------------------------------------------------
# Forecast
# ------------------------------------------------------------------
def forecast(normal, ans, kw, fuel, free_units, days=30, summer=False):
    away = ans["going_away"]
    eff = (days - away) + AWAY_SHARE * away
    mid = normal * eff * (1.15 if summer else 1.0) + EXTRA_PER_DAY["guests"] * ans["guests_next"] * min(7, days)
    lo, hi = mid * 0.9, mid * 1.1
    bills = [to_pay(u, days, kw, fuel, free_units) for u in (lo, mid, hi)]
    return (lo, mid, hi), (min(bills), bills[1], max(bills))


# ------------------------------------------------------------------
# Forecast & Analysis Helpers
# ------------------------------------------------------------------
def gj_position(units, free_units, kw=2.0, fuel=0.0, days=30):
    try:
        u = _to_num(units, 0.0)
        d = max(1, _to_int(days, 30))
        k = max(0.0, _to_num(kw, 2.0))
        f = max(0.0, _to_num(fuel, 0.0))

        in_scheme = free_units is not None and str(free_units).strip().lower() not in ("none", "nan", "")
        free_val = _to_num(free_units, None) if in_scheme else None
        if free_val is None:
            in_scheme = False

        to_free = round(free_val - u, 2) if in_scheme else None
        to_200 = round(GJ_CAP - u, 2)

        if in_scheme:
            cliff = full_bill(GJ_CAP + 1, d, k, f) - to_pay(GJ_CAP, d, k, f, free_val)
            cliff_rupees = round(cliff, 2)
        else:
            cliff_rupees = 0.0

        return {
            "in_scheme": in_scheme,
            "to_free": to_free,
            "to_200": to_200,
            "cliff_rupees": cliff_rupees,
        }
    except Exception:
        return {
            "in_scheme": False,
            "to_free": None,
            "to_200": round(GJ_CAP - _to_num(units, 0.0), 2),
            "cliff_rupees": 0.0,
        }


def forecast_next(bills, nxt=None, fuel_next=None, days=30):
    try:
        n = normal_use(bills) if bills else 0.0
        d = max(1, _to_int(days, 30))

        last = normalize_bill(bills[-1]) if bills else normalize_bill({})
        kw = last.get("load_kw", 2.0) or 2.0
        free_units = last.get("free_units")
        current_fuel = last.get("fuel_per_unit", 0.0) or 0.0

        fuel = _to_num(fuel_next, current_fuel) if fuel_next is not None else current_fuel

        nxt = nxt if isinstance(nxt, dict) else {}
        away = max(0.0, min(float(_to_int(nxt.get("away_days", 0), 0)), float(d)))
        guests = max(0.0, float(_to_int(nxt.get("guests_people", 0), 0)))
        summer = _to_bool(nxt.get("summer", False))

        eff = (d - away) + AWAY_SHARE * away
        mid = n * eff * (1.15 if summer else 1.0) + EXTRA_PER_DAY["guests"] * guests * min(7, d)
        mid = max(0.0, mid)
        lo = mid * 0.9
        hi = mid * 1.1

        b_lo = to_pay(lo, d, kw, fuel, free_units)
        b_mid = to_pay(mid, d, kw, fuel, free_units)
        b_hi = to_pay(hi, d, kw, fuel, free_units)

        r_min = min(b_lo, b_mid, b_hi)
        r_max = max(b_lo, b_mid, b_hi)

        return {
            "units": (round(lo, 2), round(mid, 2), round(hi, 2)),
            "rupees": (round(r_min, 2), round(b_mid, 2), round(r_max, 2)),
            "normal": round(n, 2),
            "fuel": round(fuel, 2),
            "over_200": bool(hi > GJ_CAP),
            "gj": gj_position(mid, free_units, kw, fuel, d),
        }
    except Exception:
        return {
            "units": (0.0, 0.0, 0.0),
            "rupees": (0.0, 0.0, 0.0),
            "normal": 0.0,
            "fuel": 0.0,
            "over_200": False,
            "gj": gj_position(0.0, None, 2.0, 0.0, 30),
        }


def fuel_shock(units, days, kw, fuel_now, fuel_new, free_units):
    try:
        u = _to_num(units, 0.0)
        d = max(1, _to_int(days, 30))
        k = max(0.0, _to_num(kw, 2.0))
        f_now = max(0.0, _to_num(fuel_now, 0.0))
        f_new = max(0.0, _to_num(fuel_new, 0.0))
        fu = _to_num(free_units, None) if free_units is not None else None

        p_new = to_pay(u, d, k, f_new, fu)
        p_now = to_pay(u, d, k, f_now, fu)
        return round(p_new - p_now, 2)
    except Exception:
        return 0.0


def rates_vs_usage(reasons):
    try:
        res = {"not_your_usage": 0.0, "your_usage": 0.0, "scheme": 0.0}
        if not reasons:
            return res
        for r in reasons:
            if not isinstance(r, dict):
                continue
            tag = r.get("tag", "")
            rupees = float(r.get("rupees", 0.0) or 0.0)
            if tag == "not your usage":
                res["not_your_usage"] += rupees
            elif tag == "your usage":
                res["your_usage"] += rupees
            elif tag == "scheme rule":
                res["scheme"] += rupees
        return {k: round(v, 2) for k, v in res.items()}
    except Exception:
        return {"not_your_usage": 0.0, "your_usage": 0.0, "scheme": 0.0}


def mid_month(units_so_far, days_so_far, days_in_cycle, kw, fuel, free_units):
    try:
        u_so_far = _to_num(units_so_far, 0.0)
        d_so_far = _to_num(days_so_far, 0.0)
        d_cycle = max(1, _to_int(days_in_cycle, 30))
        k = max(0.0, _to_num(kw, 2.0))
        f = max(0.0, _to_num(fuel, 0.0))
        fu = _to_num(free_units, None) if free_units is not None else None

        if d_so_far > 0:
            proj_units = u_so_far / d_so_far * d_cycle
        else:
            proj_units = 0.0

        proj_units = round(proj_units, 2)
        proj_rupees = round(to_pay(proj_units, d_cycle, k, f, fu), 2)

        if proj_units > GJ_CAP:
            status = "over_200"
        elif proj_units >= 0.9 * GJ_CAP:
            status = "near_200"
        else:
            status = "ok"

        return {
            "projected_units": proj_units,
            "projected_rupees": proj_rupees,
            "status": status,
        }
    except Exception:
        return {
            "projected_units": 0.0,
            "projected_rupees": 0.0,
            "status": "ok",
        }
