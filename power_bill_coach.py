"""
Power Bill Coach · Karnataka  (base version, one file)

Idea: nobody knows watts or counts appliances. So we only ask
  1. two numbers from each bill (units and days), and
  2. simple questions about what changed this month (vacation, guests, heat, ...).
The app then explains the jump in plain words, finds waste, gives tips and
forecasts the next bill.

Run:   pip install streamlit plotly
       streamlit run power_bill_coach.py
"""
import plotly.graph_objects as go
import streamlit as st

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
NEW_ITEMS = {"AC": "new_ac", "Geyser": "new_geyser", "Fridge": "new_fridge",
             "Washing machine": "new_washer", "E-scooter / EV charging": "new_ev", "Something else": "new_other"}

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
    n = int(round(x))
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
# 3. The engine: explain the jump
# ------------------------------------------------------------------
def explain(prev, cur, ans, kw, free_units):
    """prev / cur: dict(units, days, away, fuel, estimated). ans: answers for THIS bill.
    Returns list of reasons (key, units, rupees, text) that add up to the rupee change."""
    up, dp, uc, dc = prev["units"], prev["days"], cur["units"], cur["days"]

    # normal daily use, from last bill, counting away days as AWAY_SHARE of a day
    eff_prev = (dp - prev["away"]) + AWAY_SHARE * prev["away"]
    normal = up / eff_prev if eff_prev else up / dp

    # last bill estimated? then the real daily use is the average across both bills
    if prev["estimated"]:
        normal = (up + uc) / (dp + dc)

    # unit steps: what this bill would have been if only one thing changed at a time
    u_days = up * dc / dp                                      # same habits, different number of days
    eff_cur = (dc - cur["away"]) + AWAY_SHARE * cur["away"]
    u_vac = normal * eff_cur                                   # expected units after vacation / catch-up

    reasons = []
    pay = lambda u, d, f: to_pay(u, d, kw, f, free_units)
    full = lambda u, d, f: full_bill(u, d, kw, f)

    steps = [("days", u_days - up)]
    if prev["estimated"]:
        # the estimate under-billed last time, so everything beyond the extra days is catch-up
        u_vac = uc
        steps.append(("catchup", u_vac - u_days))
    elif cur["away"] != prev["away"]:
        steps.append(("vacation", u_vac - u_days))
    else:
        u_vac = u_days
    extra = uc - u_vac                                          # what is left to explain

    # share the extra between the user's "yes" answers
    weights = {}
    home_days = max(dc - cur["away"], 0)
    if ans["guests_days"] > 0 and ans["guests_people"] > 0:
        weights["guests"] = EXTRA_PER_DAY["guests"] * ans["guests_people"] * min(ans["guests_days"], home_days)
    if ans["heat"]:
        weights["heat_ac"] = EXTRA_PER_DAY["heat_ac"] * home_days * 0.5
    if ans["geyser"]:
        weights["geyser"] = EXTRA_PER_DAY["geyser"] * home_days * 0.5
    if ans["home_more"]:
        weights["home_more"] = EXTRA_PER_DAY["home_more"] * home_days * 0.6
    if ans["pump"]:
        weights["pump"] = EXTRA_PER_DAY["pump"] * home_days
    for item in ans["new_items"]:
        k = NEW_ITEMS[item]
        weights[k] = EXTRA_PER_DAY[k] * home_days * 0.7

    if extra > 0:
        expected = sum(weights.values())
        if expected > 0:
            share = min(1.0, extra / expected)          # never explain more than really happened
            for k, w in weights.items():
                steps.append((k, w * share))
            left = extra - expected * share
            if left > max(5, 0.05 * uc):
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
        before = full(run_u, dp if k == "days" else dc, prev["fuel"])
        after = full(run_u + du, dc, prev["fuel"])
        reasons.append({"key": k, "units": du, "rupees": after - before})
        run_u += du
    fuel_r = full(uc, dc, cur["fuel"]) - full(uc, dc, prev["fuel"])
    if abs(fuel_r) >= 1:
        reasons.append({"key": "fuel", "units": 0, "rupees": fuel_r})
    gj_r = (pay(uc, dc, cur["fuel"]) - full(uc, dc, cur["fuel"])) - (pay(up, dp, prev["fuel"]) - full(up, dp, prev["fuel"]))
    if abs(gj_r) >= 1:
        reasons.append({"key": "gj", "units": 0, "rupees": gj_r})

    reasons = [r for r in reasons if abs(r["rupees"]) >= 1 or abs(r["units"]) >= 1]
    for r in reasons:
        r["text"] = reason_text(r, prev, cur, ans, normal, free_units)
    reasons.sort(key=lambda r: -abs(r["rupees"]))
    total = pay(uc, dc, cur["fuel"]) - pay(up, dp, prev["fuel"])
    return reasons, total, normal


def reason_text(r, prev, cur, ans, normal, free_units):
    k, u = r["key"], abs(r["units"])
    if k == "days":
        d = cur["days"] - prev["days"]
        return (f"This bill covered {abs(d)} {'more' if d > 0 else 'fewer'} day{'s' if abs(d) != 1 else ''} "
                f"than last time. Same habits, {'longer' if d > 0 else 'shorter'} bill.")
    if k == "vacation":
        if cur["away"] > prev["away"]:
            return f"You were away {cur['away']} days this time, so you used about {u:.0f} units less."
        return f"Last time you were away {prev['away']} days. This time you were home more, so about {u:.0f} units more."
    if k == "catchup":
        return ("Last bill was an ESTIMATE (meter not read). This bill catches up the real units. "
                f"Your real use was about {normal:.1f} units a day, which is normal.")
    if k == "guests":
        return f"{ans['guests_people']} guest(s) for {ans['guests_days']} days added about {u:.0f} units."
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
                 "new_other": "new appliance"}[k]
        return f"Your {thing} added about {u:.0f} units."
    if k == "unknown":
        return (f"About {u:.0f} units are not explained by your answers. Something new is using power: "
                "check the water motor, geyser left on, an old fridge, or an inverter.")
    if k == "less":
        return f"You used about {u:.0f} units less than normal. Well done."
    if k == "fuel":
        return "The fuel surcharge (FPPCA) went up. Not your fault: coal and gas cost more."
    if k == "gj":
        if cur["units"] > GJ_CAP and free_units is not None:
            return f"You crossed 200 units ({cur['units']:.0f}), so Gruha Jyothi stopped for this month. Full bill payable."
        if r["rupees"] > 0:
            return f"You went past your {free_units:.0f} free Gruha Jyothi units, so you pay for the extra units."
        return "You came back within your free Gruha Jyothi units."
    return ""


# ------------------------------------------------------------------
# 4. Waste finder, tips and forecast
# ------------------------------------------------------------------
def waste_checks(prev, cur, normal, reasons, free_units):
    out = []
    # Vacation test: away many days but the bill did not drop
    if cur["away"] >= 5:
        home_only = normal * (cur["days"] - cur["away"])
        away_units = max(cur["units"] - home_only, 0) if not prev["estimated"] else None
        expected_away = normal * AWAY_SHARE * cur["away"]
        if away_units is not None and away_units > 1.6 * expected_away:
            per_day = away_units / cur["away"]
            out.append(("danger",
                        f"Vacation test FAILED: you were away {cur['away']} days but the home still used about "
                        f"{per_day:.1f} units a day. Something stays ON when nobody is home: water motor, geyser, "
                        "an old fridge, inverter or a light. Switch off at the mains next time you travel."))
        else:
            out.append(("ok", f"Vacation test passed: while you were away the home used very little. Good."))
    unk = [r for r in reasons if r["key"] == "unknown"]
    if unk:
        out.append(("warn", f"{unk[0]['units']:.0f} units have no reason. That is about "
                            f"{rupees(unk[0]['units'] * RATE * (1 + TAX))} you may be wasting. "
                            "Try this: switch off everything at night and read the meter. In the morning, "
                            "if more than 1 unit has gone, something is leaking power."))
    if prev["estimated"]:
        out.append(("info", "Your last bill was an estimate. Ask BESCOM for a real meter reading every month "
                            "(call 1912 or use the BESCOM Mithra app) so you do not get one big catch-up bill."))
    if free_units is not None and GJ_CAP - 15 <= cur["units"] <= GJ_CAP + 15:
        out.append(("warn", f"You are very close to the 200-unit line ({cur['units']:.0f} units). "
                            "A few units decide whether you pay ₹0 or the full bill."))
    if not out:
        out.append(("ok", "No waste found from your answers. Your use looks normal."))
    return out


def tips(ans, cur, free_units, full_now):
    t = []
    if free_units is not None and cur["units"] > GJ_CAP:
        over = cur["units"] - GJ_CAP
        t.append((f"You were only {over:.0f} units over 200. That is {over / cur['days']:.1f} units a day. "
                  f"Staying under would have saved {rupees(full_now)} this month.", "Free"))
    if ans["heat"]:
        t.append(("Set the AC to 24°C or 25°C instead of 18°C to 21°C. Each degree up saves about 6% of AC power.", "Free"))
    if ans["geyser"]:
        t.append(("Switch the geyser off right after bathing, or fit a timer.", "Free to ₹300"))
    if ans["pump"]:
        t.append(("Fit an automatic cut-off on the water motor so the tank never overflows.", "About ₹400"))
    if ans["guests_days"] > 0:
        t.append(("With guests at home, run the washing machine with full loads only and avoid ironing daily.", "Free"))
    if cur["away"] > 0 or ans["going_away"] > 0:
        t.append(("Before travelling: switch off the geyser, water motor, Wi-Fi and TV at the mains. Keep only the fridge on.", "Free"))
    if "E-scooter / EV charging" in ans["new_items"]:
        t.append(("Charge the e-scooter only till 80 to 90% and unplug when done.", "Free"))
    t.append(("Switch off the set-top box at the plug at night.", "Free"))
    t.append(("Read your meter on the 15th. The app will tell you if you are heading over 200 units.", "Free"))
    return t


def forecast(normal, ans, kw, fuel, free_units, days=30, summer=False):
    away = ans["going_away"]
    eff = (days - away) + AWAY_SHARE * away
    mid = normal * eff * (1.15 if summer else 1.0) + EXTRA_PER_DAY["guests"] * ans["guests_next"] * min(7, days)
    lo, hi = mid * 0.9, mid * 1.1
    bills = [to_pay(u, days, kw, fuel, free_units) for u in (lo, mid, hi)]
    return (lo, mid, hi), (min(bills), bills[1], max(bills))


# ------------------------------------------------------------------
# 5. Examples for the demo
# ------------------------------------------------------------------
EXAMPLES = {
    "Dasara guests (Gruha Jyothi family)": dict(
        pu=168, pd=30, pa=0, pe=False, cu=206, cd=31, ca=0, kw=2.0, free=150, pf=0.0, cf=0.37,
        guests_days=8, guests_people=3, heat=False, geyser=True, home_more=False, pump=False, new_items=[],
        going_away=0, guests_next=0),
    "Went on vacation, bill did not drop": dict(
        pu=240, pd=30, pa=0, pe=False, cu=232, cd=31, ca=12, kw=3.0, free=None, pf=0.0, cf=0.0,
        guests_days=0, guests_people=0, heat=False, geyser=False, home_more=False, pump=False, new_items=[],
        going_away=0, guests_next=0),
    "Door-lock estimated bill": dict(
        pu=180, pd=29, pa=0, pe=True, cu=352, cd=33, ca=0, kw=4.0, free=None, pf=0.0, cf=0.0,
        guests_days=0, guests_people=0, heat=False, geyser=False, home_more=False, pump=False, new_items=[],
        going_away=0, guests_next=0),
    "Summer + new AC": dict(
        pu=140, pd=31, pa=0, pe=False, cu=265, cd=30, ca=0, kw=3.0, free=None, pf=0.0, cf=0.0,
        guests_days=0, guests_people=0, heat=True, geyser=False, home_more=True, pump=False, new_items=["AC"],
        going_away=0, guests_next=0),
    "Start blank": dict(
        pu=150, pd=30, pa=0, pe=False, cu=150, cd=30, ca=0, kw=2.0, free=None, pf=0.0, cf=0.0,
        guests_days=0, guests_people=0, heat=False, geyser=False, home_more=False, pump=False, new_items=[],
        going_away=0, guests_next=0),
}

# ------------------------------------------------------------------
# 6. The page
# ------------------------------------------------------------------
st.set_page_config(page_title="Power Bill Coach · Karnataka", page_icon="⚡", layout="wide")
st.title("⚡ Power Bill Coach · Karnataka")
st.caption("Your BESCOM bill, explained like a friend would. No watts, no appliance lists. Just a few questions.")

ex_name = st.selectbox("Try an example, or start blank", list(EXAMPLES))
E = EXAMPLES[ex_name]
K = lambda name: f"{ex_name}:{name}"     # new widget keys per example, so values reset

st.header("Step 1 · Two numbers from each bill")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Last bill")
    pu = st.number_input("Units", 0.0, 5000.0, float(E["pu"]), key=K("pu"))
    pd_ = st.number_input("Days in the bill", 20, 45, E["pd"], key=K("pd"))
    pa = st.number_input("Days nobody was home (vacation)", 0, 45, E["pa"], key=K("pa"))
    pe = st.checkbox("This bill was an ESTIMATE / door lock / average", E["pe"], key=K("pe"))
with c2:
    st.subheader("This bill")
    cu = st.number_input("Units ", 0.0, 5000.0, float(E["cu"]), key=K("cu"))
    cd = st.number_input("Days in the bill ", 20, 45, E["cd"], key=K("cd"))
    ca = st.number_input("Days nobody was home (vacation) ", 0, 45, E["ca"], key=K("ca"))
with st.expander("More bill details (optional)"):
    a, b_, c = st.columns(3)
    kw = a.number_input("Sanctioned load (kW)", 0.5, 20.0, E["kw"], 0.5, key=K("kw"))
    in_gj = b_.checkbox("We are in Gruha Jyothi", E["free"] is not None, key=K("gj"))
    free = b_.number_input("Free units printed on the bill", 0, 200, E["free"] or 150, key=K("free")) if in_gj else None
    pf = c.number_input("Fuel surcharge last bill (₹/unit)", 0.0, 3.0, E["pf"], 0.01, key=K("pf"))
    cf = c.number_input("Fuel surcharge this bill (₹/unit)", 0.0, 3.0, E["cf"], 0.01, key=K("cf"))

st.header("Step 2 · What was different this month?")
q1, q2 = st.columns(2)
with q1:
    g_people = st.number_input("How many guests stayed? (0 if none)", 0, 20, E["guests_people"], key=K("gp"))
    g_days = st.number_input("For how many days?", 0, 45, E["guests_days"], key=K("gd")) if g_people else 0
    heat = st.checkbox("It was hot and we used AC / cooler / fans more", E["heat"], key=K("heat"))
    geyser = st.checkbox("It was cold or rainy and we used the geyser more", E["geyser"], key=K("gey"))
with q2:
    home_more = st.checkbox("More people at home in the day (school holidays / work from home)", E["home_more"], key=K("hm"))
    pump = st.checkbox("The water motor ran more (water problem / tank overflow)", E["pump"], key=K("pump"))
    new_items = st.multiselect("Did you buy or start using something new?", list(NEW_ITEMS), E["new_items"], key=K("new"))

prev = {"units": pu, "days": pd_, "away": pa, "fuel": pf, "estimated": pe}
cur = {"units": cu, "days": cd, "away": ca, "fuel": cf, "estimated": False}
ans = {"guests_people": g_people, "guests_days": g_days, "heat": heat, "geyser": geyser,
       "home_more": home_more, "pump": pump, "new_items": new_items, "going_away": 0, "guests_next": 0}

reasons, total, normal = explain(prev, cur, ans, kw, free)
pay_prev = to_pay(pu, pd_, kw, pf, free)
pay_cur = to_pay(cu, cd, kw, cf, free)

st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("This bill", rupees(pay_cur), rupees(total), delta_color="inverse")
m2.metric("Last bill", rupees(pay_prev))
m3.metric("Your normal use", f"{normal:.1f} units/day")
m4.metric("Gruha Jyothi", "Not in scheme" if free is None else ("Lost (200+)" if cu > GJ_CAP else
          ("Free" if cu <= free else "Partly free")))

# ---- Insight 1
with st.container(border=True):
    st.subheader("1 · Why your bill changed")
    if abs(total) < 20:
        st.markdown("#### Your bill is about the same as last time.")
    else:
        st.markdown(f"#### Your bill went {'up' if total > 0 else 'down'} by {rupees(abs(total))}.")
    if reasons:
        st.markdown(f"**Biggest reason: {LABEL[reasons[0]['key']]}**")
    left, right = st.columns([1.1, 1])
    with left:
        for r in reasons:
            colr = "#c2410c" if r["rupees"] > 0 else "#1b8a5a"
            tag = "not your usage" if r["key"] in NOT_YOUR_USAGE else ("scheme rule" if r["key"] == "gj" else "your usage")
            st.markdown(f"<div style='border-left:4px solid {colr};padding:4px 10px;margin:6px 0'>"
                        f"<b>{LABEL[r['key']]}: {'+' if r['rupees'] > 0 else ''}{rupees(r['rupees'])}</b> "
                        f"<span style='color:#6b7280;font-size:0.85em'>({tag})</span><br>{r['text']}</div>",
                        unsafe_allow_html=True)
    with right:
        fig = go.Figure(go.Waterfall(
            x=["Last bill"] + [LABEL[r["key"]] for r in reasons] + ["This bill"],
            measure=["absolute"] + ["relative"] * len(reasons) + ["total"],
            y=[pay_prev] + [r["rupees"] for r in reasons] + [0],
            text=[rupees(pay_prev)] + [rupees(r["rupees"]) for r in reasons] + [rupees(pay_cur)],
            textposition="outside", increasing={"marker": {"color": "#c2410c"}},
            decreasing={"marker": {"color": "#1b8a5a"}}, totals={"marker": {"color": "#2563eb"}}))
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig, width="stretch")

# ---- Insight 2
with st.container(border=True):
    st.subheader("2 · Where the waste is")
    for level, text in waste_checks(prev, cur, normal, reasons, free):
        {"danger": st.error, "warn": st.warning, "info": st.info, "ok": st.success}[level](text)

# ---- Insight 3
with st.container(border=True):
    st.subheader("3 · How to save")
    for text, cost in tips(ans, cur, free, full_bill(cu, cd, kw, cf))[:5]:
        st.markdown(f"✅ **{text}**  \n<span style='color:#6b7280'>Cost: {cost}</span>", unsafe_allow_html=True)

# ---- Forecast
with st.container(border=True):
    st.subheader("Next bill forecast")
    f1, f2, f3, f4 = st.columns(4)
    going_away = f1.number_input("Days you will be away next month", 0, 31, 0, key=K("ga"))
    guests_next = f2.number_input("Guests expected next month", 0, 20, 0, key=K("gn"))
    summer = f3.checkbox("Next month is summer (Mar to May)", key=K("su"))
    fuel_next = f4.number_input("Fuel surcharge next month (₹/unit)", 0.0, 3.0, cf, 0.05, key=K("fn"),
                                help="Try ₹1.00 to see what a fuel shock (e.g. a Strait of Hormuz crisis) would do.")
    ans_next = dict(ans, going_away=going_away, guests_next=guests_next)
    (lo_u, mid_u, hi_u), (lo, mid, hi) = forecast(normal, ans_next, kw, fuel_next, free, summer=summer)
    st.markdown(f"### {rupees(lo)} to {rupees(hi)}")
    st.caption(f"About {lo_u:.0f} to {hi_u:.0f} units if your habits stay normal. Most likely {rupees(mid)}.")
    if fuel_next > cf:
        base = forecast(normal, ans_next, kw, cf, free, summer=summer)[1][1]
        st.warning(f"A fuel price shock adds about {rupees(mid - base)} with the SAME usage. That part is not your fault.")
    if free is not None and hi_u > GJ_CAP:
        st.error(f"Risk: you may cross 200 units and lose Gruha Jyothi. Keep under {GJ_CAP / 30:.1f} units a day.")

    st.markdown("**Mid-month check: read your meter today**")
    g1, g2 = st.columns(2)
    so_far = g1.number_input("Units used since last bill", 0, 2000, int(normal * 15), key=K("sf"))
    d_so_far = g2.number_input("Days since last bill", 1, 40, 15, key=K("ds"))
    proj = so_far / d_so_far * 30
    if free is not None and proj > GJ_CAP:
        st.error(f"At this pace: about {proj:.0f} units. You will LOSE Gruha Jyothi. "
                 f"Stay under {max(GJ_CAP - so_far, 0) / max(30 - d_so_far, 1):.1f} units a day for the rest of the month.")
    elif free is not None and proj > free:
        st.warning(f"At this pace: about {proj:.0f} units, above your {free} free units. "
                   f"Stay under {max(free - so_far, 0) / max(30 - d_so_far, 1):.1f} units a day to keep it free.")
    else:
        st.success(f"At this pace: about {proj:.0f} units this month. Bill about {rupees(to_pay(proj, 30, kw, cf, free))}.")

st.caption("Rates used: ₹5.80/unit, ₹150/kW/month fixed, 9% tax. Check against your BESCOM bill. "
           "Typical values are only used to share out extra units between your answers, never shown as exact.")
