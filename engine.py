"""
Power Bill Coach · Engine (pure Python, no UI dependencies)
Bill calculation, explanation, forecasting, and historical usage analysis.
"""

# ------------------------------------------------------------------
# 1. BESCOM numbers (check against a real bill and fix here)
# ------------------------------------------------------------------
RATE = 5.80          # Rs per unit, BESCOM domestic, flat
FIXED_PER_KW = 150   # Rs per kW per month
TAX = 0.09           # tax on the energy charge
GJ_CAP = 200         # Gruha Jyothi: above 200 units the full bill is payable

# How much a home uses on a day when nobody is there (fridge, Wi-Fi, standby),
# as a share of a normal day. Used for the vacation logic.
AWAY_SHARE = 0.30

# Hidden typical extra units PER DAY for each "yes" answer.
# The user never sees or enters these. They are only used to share out the
# extra units between the reasons the user ticked.
EXTRA_PER_DAY = {
    "guests": 1.2,        # per extra person
    "heat_ac": 3.0,       # AC / cooler used more
    "geyser": 1.0,        # geyser used more (cold or rainy weather)
    "home_more": 1.5,     # kids on holidays / work from home
    "pump": 0.4,          # water motor ran more
    "new_ac": 3.0, "new_geyser": 1.0, "new_fridge": 1.0, "new_washer": 0.3,
    "new_ev": 2.0,        # e-scooter charging at home
    "new_other": 0.8,
}
NEW_ITEMS = {
    "AC": "new_ac", "Geyser": "new_geyser", "Fridge": "new_fridge",
    "Washing machine": "new_washer", "E-scooter / EV charging": "new_ev", "Something else": "new_other"
}

LABEL = {
    "days": "Billing days", "vacation": "Vacation / away days", "catchup": "Meter catch-up",
    "guests": "Guests at home", "heat_ac": "Hot weather (AC / cooler)", "geyser": "Geyser use",
    "home_more": "More people at home in the day", "pump": "Water motor", "unknown": "Not explained yet",
    "less": "You used less", "fuel": "Fuel surcharge", "gj": "Gruha Jyothi",
    "new_ac": "New AC", "new_geyser": "New geyser", "new_fridge": "New fridge", "new_washer": "New washing machine",
    "new_ev": "EV / e-scooter charging", "new_other": "New appliance",
}
NOT_YOUR_USAGE = {"days", "catchup", "fuel"}


def rupees(x):
    if x is None:
        return "₹0"
    try:
        n = int(round(x))
    except (ValueError, TypeError):
        return "₹0"
    s = str(abs(n))
    if len(s) > 3:
        head, tail, parts = s[:-3], s[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        s = (",".join([head] + parts) if head else ",".join(parts)) + "," + tail
    return ("-" if n < 0 else "") + "₹" + s


# ------------------------------------------------------------------
# 2. Bill math
# ------------------------------------------------------------------
def full_bill(units, days, kw, fuel):
    units = 0.0 if units is None else float(units)
    days = 0.0 if days is None else float(days)
    kw = 0.0 if kw is None else float(kw)
    fuel = 0.0 if fuel is None else float(fuel)
    energy = units * RATE
    return energy + kw * FIXED_PER_KW * days / 30 + units * fuel + energy * TAX


def to_pay(units, days, kw, fuel, free_units):
    """What the family actually pays after Gruha Jyothi."""
    units = 0.0 if units is None else float(units)
    days = 0.0 if days is None else float(days)
    kw = 0.0 if kw is None else float(kw)
    fuel = 0.0 if fuel is None else float(fuel)
    full = full_bill(units, days, kw, fuel)
    if free_units is None or units > GJ_CAP:
        return full
    if units <= free_units:
        return 0.0
    extra = units - free_units
    return extra * (RATE * (1 + TAX) + fuel)   # only the extra units, no fixed charge


# ------------------------------------------------------------------
# 3. Historical baseline & conversions
# ------------------------------------------------------------------
def normal_daily(history):
    """Average daily usage over the last 1 to 6 bills from history (excluding current)."""
    if not history:
        return 0.0
    bills = list(history)[-6:]
    if not bills:
        return 0.0
    real_bills = [b for b in bills if isinstance(b, dict) and not b.get("estimated", False)]
    candidates = real_bills if len(real_bills) >= 2 else [b for b in bills if isinstance(b, dict)]
    dailies = []
    for b in candidates:
        try:
            units = float(b.get("units", 0.0) or 0.0)
            days = float(b.get("days", 0.0) or 0.0)
            away = float(b.get("away", 0.0) or 0.0)
        except (ValueError, TypeError):
            continue
        eff_days = (days - away) + AWAY_SHARE * away
        daily = (units / eff_days) if eff_days > 0 else 0.0
        dailies.append(daily)
    if not dailies:
        return 0.0
    return sum(dailies) / len(dailies)


def bills_to_prev_cur(db_rows):
    """Convert db.get_bills() rows into (prev, cur, history). Returns None if < 2 rows."""
    if db_rows is None or len(db_rows) < 2:
        return None
    converted = []
    for row in db_rows:
        try:
            r = dict(row)
        except Exception:
            continue
        r["away"] = r.get("away", 0) if r.get("away") is not None else 0
        r["fuel"] = r.get("fuel_rs", r.get("fuel", 0.0))
        if r["fuel"] is None:
            r["fuel"] = 0.0
        converted.append(r)
    if len(converted) < 2:
        return None
    prev = converted[-2]
    cur = converted[-1]
    history = converted[:-2]
    return prev, cur, history


# ------------------------------------------------------------------
# 4. The engine: explain the jump
# ------------------------------------------------------------------
def explain(prev, cur, ans, kw, free_units, history=None):
    """prev / cur: dict(units, days, away, fuel, estimated). ans: answers for THIS bill.
    Returns list of reasons (key, units, rupees, text) that add up to the rupee change."""
    prev = prev or {}
    cur = cur or {}
    ans = ans or {}
    kw = 0.0 if kw is None else float(kw)
    up = float(prev.get("units", 0.0) or 0.0)
    dp = float(prev.get("days", 0.0) or 0.0)
    uc = float(cur.get("units", 0.0) or 0.0)
    dc = float(cur.get("days", 0.0) or 0.0)
    prev_away = float(prev.get("away", 0.0) or 0.0)
    cur_away = float(cur.get("away", 0.0) or 0.0)
    prev_fuel = float(prev.get("fuel", 0.0) or 0.0)
    cur_fuel = float(cur.get("fuel", 0.0) or 0.0)
    prev_est = bool(prev.get("estimated", False))

    if history is not None:
        normal = normal_daily(history)
    else:
        # normal daily use, from last bill, counting away days as AWAY_SHARE of a day
        eff_prev = (dp - prev_away) + AWAY_SHARE * prev_away
        normal = up / eff_prev if eff_prev else (up / dp if dp else 0.0)

        # last bill estimated? then the real daily use is the average across both bills
        if prev_est:
            normal = (up + uc) / (dp + dc) if (dp + dc) else 0.0

    # unit steps: what this bill would have been if only one thing changed at a time
    u_days = (up * dc / dp) if dp else 0.0                      # same habits, different number of days
    eff_cur = (dc - cur_away) + AWAY_SHARE * cur_away
    u_vac = normal * eff_cur                                   # expected units after vacation / catch-up

    reasons = []
    pay = lambda u, d, f: to_pay(u, d, kw, f, free_units)
    full = lambda u, d, f: full_bill(u, d, kw, f)

    steps = [("days", u_days - up)]
    if prev_est:
        # the estimate under-billed last time, so everything beyond the extra days is catch-up
        u_vac = uc
        steps.append(("catchup", u_vac - u_days))
    elif cur_away != prev_away:
        steps.append(("vacation", u_vac - u_days))
    else:
        u_vac = u_days
    extra = uc - u_vac                                          # what is left to explain

    # share the extra between the user's "yes" answers
    weights = {}
    home_days = max(dc - cur_away, 0.0)
    guests_days = float(ans.get("guests_days", 0) or 0)
    guests_people = float(ans.get("guests_people", 0) or 0)
    if guests_days > 0 and guests_people > 0:
        weights["guests"] = EXTRA_PER_DAY["guests"] * guests_people * min(guests_days, home_days)
    if ans.get("heat"):
        weights["heat_ac"] = EXTRA_PER_DAY["heat_ac"] * home_days * 0.5
    if ans.get("geyser"):
        weights["geyser"] = EXTRA_PER_DAY["geyser"] * home_days * 0.5
    if ans.get("home_more"):
        weights["home_more"] = EXTRA_PER_DAY["home_more"] * home_days * 0.6
    if ans.get("pump"):
        weights["pump"] = EXTRA_PER_DAY["pump"] * home_days
    for item in ans.get("new_items", []) or []:
        if item in NEW_ITEMS:
            k = NEW_ITEMS[item]
            weights[k] = EXTRA_PER_DAY[k] * home_days * 0.7

    if extra > 0:
        expected = sum(weights.values())
        if expected > 0:
            share = min(1.0, extra / expected)          # never explain more than really happened
            for k, w in weights.items():
                steps.append((k, w * share))
            left = extra - expected * share
            if left > max(5.0, 0.05 * uc):
                steps.append(("unknown", left))
            elif left > 0:
                # tiny leftover: give it to the biggest answer so totals match
                big = max(weights, key=weights.get)
                steps = [(k, v + left) if k == big else (k, v) for k, v in steps]
        else:
            steps.append(("unknown", extra))
    elif extra < 0:
        steps.append(("less", extra))

    # turn unit steps into rupees (full bill, last bill's fuel), then fuel, then Gruha Jyothi
    run_u = up
    for k, du in steps:
        before = full(run_u, dp if k == "days" else dc, prev_fuel)
        after = full(run_u + du, dc, prev_fuel)
        reasons.append({"key": k, "units": du, "rupees": after - before})
        run_u += du
    fuel_r = full(uc, dc, cur_fuel) - full(uc, dc, prev_fuel)
    if abs(fuel_r) >= 1:
        reasons.append({"key": "fuel", "units": 0.0, "rupees": fuel_r})
    gj_r = (pay(uc, dc, cur_fuel) - full(uc, dc, cur_fuel)) - (pay(up, dp, prev_fuel) - full(up, dp, prev_fuel))
    if abs(gj_r) >= 1:
        reasons.append({"key": "gj", "units": 0.0, "rupees": gj_r})

    reasons = [r for r in reasons if abs(r["rupees"]) >= 1 or abs(r["units"]) >= 1]
    for r in reasons:
        r["text"] = reason_text(r, prev, cur, ans, normal, free_units)
    reasons.sort(key=lambda r: -abs(r["rupees"]))
    total = pay(uc, dc, cur_fuel) - pay(up, dp, prev_fuel)
    return reasons, total, normal


def reason_text(r, prev, cur, ans, normal, free_units):
    prev = prev or {}
    cur = cur or {}
    ans = ans or {}
    normal = float(normal or 0.0)
    k, u = r["key"], abs(r["units"])
    if k == "days":
        d = (cur.get("days", 0) or 0) - (prev.get("days", 0) or 0)
        return (f"This bill covered {abs(d)} {'more' if d > 0 else 'fewer'} day{'s' if abs(d) != 1 else ''} "
                f"than last time. Same habits, {'longer' if d > 0 else 'shorter'} bill.")
    if k == "vacation":
        cur_away = cur.get("away", 0) or 0
        prev_away = prev.get("away", 0) or 0
        if cur_away > prev_away:
            return f"You were away {cur_away} days this time, so you used about {u:.0f} units less."
        return f"Last time you were away {prev_away} days. This time you were home more, so about {u:.0f} units more."
    if k == "catchup":
        return ("Last bill was an ESTIMATE (meter not read). This bill catches up the real units. "
                f"Your real use was about {normal:.1f} units a day, which is normal.")
    if k == "guests":
        guests_people = ans.get("guests_people", 0) or 0
        guests_days = ans.get("guests_days", 0) or 0
        return f"{guests_people} guest(s) for {guests_days} days added about {u:.0f} units."
    if k == "heat_ac":
        return f"More AC / cooler / fan in the heat added about {u:.0f} units."
    if k == "geyser":
        return f"More geyser use added about {u:.0f} units."
    if k == "home_more":
        return f"More people at home during the day (holidays / work from home) added about {u:.0f} units."
    if k == "pump":
        return f"The water motor running more added about {u:.0f} units."
    if k.startswith("new_"):
        thing = {"new_ac": "new AC", "new_geyser": "new geyser", "new_fridge": "new fridge",
                 "new_washer": "new washing machine", "new_ev": "EV / e-scooter charging",
                 "new_other": "new appliance"}.get(k, "new appliance")
        return f"Your {thing} added about {u:.0f} units."
    if k == "unknown":
        return (f"About {u:.0f} units are not explained by your answers. Something new is using power: "
                "check the water motor, geyser left on, an old fridge, or an inverter.")
    if k == "less":
        return f"You used about {u:.0f} units less than normal. Well done."
    if k == "fuel":
        return "The fuel surcharge (FPPCA) went up. Not your fault: coal and gas cost more."
    if k == "gj":
        cur_units = float(cur.get("units", 0) or 0)
        if cur_units > GJ_CAP and free_units is not None:
            return f"You crossed 200 units ({cur_units:.0f}), so Gruha Jyothi stopped for this month. Full bill payable."
        if r.get("rupees", 0) > 0:
            free_str = f"{free_units:.0f}" if free_units is not None else "0"
            return f"You went past your {free_str} free Gruha Jyothi units, so you pay for the extra units."
        return "You came back within your free Gruha Jyothi units."
    return ""


# ------------------------------------------------------------------
# 5. Forecast
# ------------------------------------------------------------------
def forecast(normal, ans, kw, fuel, free_units, days=30, summer=False):
    ans = ans or {}
    normal = float(normal or 0.0)
    days = float(days or 0.0)
    kw = float(kw or 0.0)
    fuel = float(fuel or 0.0)
    away = float(ans.get("going_away", 0) or 0)
    eff = (days - away) + AWAY_SHARE * away
    guests_next = float(ans.get("guests_next", 0) or 0)
    mid = normal * eff * (1.15 if summer else 1.0) + EXTRA_PER_DAY["guests"] * guests_next * min(7.0, days)
    lo, hi = mid * 0.9, mid * 1.1
    bills = [to_pay(u, days, kw, fuel, free_units) for u in (lo, mid, hi)]
    return (lo, mid, hi), (min(bills), bills[1], max(bills))
