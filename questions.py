"""
questions.py - Question list, waste finder, and saving tips for Power Bill Coach.

Part of HackNova-26, Problem P01.
Shared Contract:
- engine.RATE = 5.80, engine.FIXED_PER_KW = 150, engine.TAX = 0.09
- engine.GJ_CAP = 200, engine.AWAY_SHARE = 0.30
- engine.full_bill(units, days, kw, fuel) -> rupees (no Gruha Jyothi)
- engine.to_pay(units, days, kw, fuel, free_units) -> rupees after Gruha Jyothi
- engine.normal_use(bills) -> units per day (avg of last 3-6 bills)
- engine.explain(bills, answers) -> (reasons, total, normal)
- db.get_bills(user_id) -> list of bill dicts (old -> new)
- text.T(key, lang) -> translated text in 'en' or 'kn'

Functions implemented here:
- QUESTIONS: The 9 household questions.
- waste_checks(bills, answers, normal) -> list of (level, message, numbers)
- tips(answers, bills) -> ranked list of (message, units_saved_range, rupees_range, cost, who)
"""

from typing import Any, Dict, List, Optional, Tuple, Union

# -----------------------------------------------------------------------------
# Shared Imports (engine is stable — fail loudly if missing)
# -----------------------------------------------------------------------------
from engine import (
    RATE,
    FIXED_PER_KW,
    TAX,
    GJ_CAP,
    AWAY_SHARE,
    full_bill,
    to_pay,
    normal_use,
    explain,
)

from text import T


# -----------------------------------------------------------------------------
# Rupee Formatter (Indian Numbering Format)
# -----------------------------------------------------------------------------
def rupees(x: Union[int, float]) -> str:
    """Format number into Indian Rupee representation (e.g. ₹1,250)."""
    if x is None:
        return "₹0"
    try:
        n = int(round(float(x)))
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


# -----------------------------------------------------------------------------
# 1) QUESTIONS: The 9 Household Questions
# -----------------------------------------------------------------------------
NEW_APPLIANCE_OPTIONS = [
    "AC",
    "Geyser",
    "Fridge",
    "Washing machine",
    "EV / e-scooter",
    "Other"
]

QUESTIONS = [
    {
        "key": "vacation_days",
        "label_key": "q_vacation_days",
        "label": "Were you away from home for several days? (vacation / travel)",
        "type": "number",
        "min": 0,
        "max": 45,
        "default": 0,
        "help": "Number of days nobody was home (enter 0 if you were not away)."
    },
    {
        "key": "guests",
        "label_key": "q_guests",
        "label": "Did you have guests staying over?",
        "type": "guests_group",
        "subkeys": {
            "people": "guests_people",
            "days": "guests_days"
        },
        "default_people": 0,
        "default_days": 0,
        "help": "More hot showers, laundry, fans/AC, and cooking add extra units."
    },
    {
        "key": "hot_ac",
        "label_key": "q_hot_ac",
        "label": "Was the weather unusually hot, so you used AC / cooler / fans more?",
        "type": "yes_no",
        "default": False,
        "help": "Air conditioners and coolers are the largest driver of hot-weather bill jumps."
    },
    {
        "key": "geyser",
        "label_key": "q_geyser",
        "label": "Was it cold or rainy, so you used the geyser / water heater more?",
        "type": "yes_no",
        "default": False,
        "help": "Water heating draws 2,000 watts; extra baths or reheating add units rapidly."
    },
    {
        "key": "home_more",
        "label_key": "q_home_more",
        "label": "Was someone home during the day more than usual? (holidays / WFH)",
        "type": "yes_no",
        "default": False,
        "help": "Daytime occupancy adds lights, laptops, fans, TV, and fridge door openings."
    },
    {
        "key": "pump",
        "label_key": "q_pump",
        "label": "Did you use the water motor more frequently? (tanker water / tank overflow)",
        "type": "yes_no",
        "default": False,
        "help": "Frequent motor cycles or undetected roof-tank overflows waste power."
    },
    {
        "key": "new_items",
        "label_key": "q_new_items",
        "label": "Did you purchase or start using any new electrical appliance?",
        "type": "multiselect",
        "options": NEW_APPLIANCE_OPTIONS,
        "default": [],
        "help": "Select any new appliances added this billing month."
    },
    {
        "key": "festival_lights",
        "label_key": "q_festival_lights",
        "label": "Did you use festival, wedding, or decorative lighting?",
        "type": "yes_no",
        "default": False,
        "help": "Outdoor string lights running for hours every evening."
    },
    {
        "key": "power_cuts",
        "label_key": "q_power_cuts",
        "label": "Were there frequent power cuts, causing the inverter battery to charge more?",
        "type": "yes_no",
        "default": False,
        "help": "Inverters draw heavy recharge current after outages; worn batteries stay charging."
    }
]


def normalize_answers(answers: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure answers dictionary contains standard keys with safe types and defaults."""
    if not isinstance(answers, dict):
        answers = {}

    vacation_days = int(answers.get("vacation_days", answers.get("away_days", 0)) or 0)
    vacation_days = max(vacation_days, 0)

    guests_people = int(answers.get("guests_people", 0) or 0)
    guests_days = int(answers.get("guests_days", 0) or 0)
    if answers.get("guests") and guests_people <= 0:
        guests_people = 2
    if answers.get("guests") and guests_days <= 0:
        guests_days = 5

    raw_items = answers.get("new_items", [])
    if isinstance(raw_items, str):
        raw_items = [raw_items]
    elif not isinstance(raw_items, (list, tuple)):
        raw_items = []
    clean_items = [it for it in raw_items if it in NEW_APPLIANCE_OPTIONS]

    hot_ac = bool(answers.get("hot_ac", answers.get("heat", False)))

    return {
        "vacation_days": vacation_days,
        "away_days": vacation_days,
        "away": vacation_days > 0,
        "guests": (guests_people > 0 and guests_days > 0) or bool(answers.get("guests", False)),
        "guests_people": max(guests_people, 0),
        "guests_days": max(guests_days, 0),
        "hot_ac": hot_ac,
        "heat": hot_ac,
        "geyser": bool(answers.get("geyser", False)),
        "home_more": bool(answers.get("home_more", False)),
        "pump": bool(answers.get("pump", False)),
        "new_items": clean_items,
        "new_appliance": len(clean_items) > 0,
        "festival_lights": bool(answers.get("festival_lights", False)),
        "power_cuts": bool(answers.get("power_cuts", False)),
        "going_away": int(answers.get("going_away", 0) or 0),
        "guests_next": int(answers.get("guests_next", 0) or 0),
    }


# -----------------------------------------------------------------------------
# 2) waste_checks(bills, answers, normal) -> list of (level, message, numbers)
# -----------------------------------------------------------------------------
class WasteCheckResult(tuple):
    """
    3-tuple (level, message, numbers) supporting:
      - 3-tuple unpacking: level, message, numbers = item
      - 2-tuple unpacking (legacy): level, message = item
      - attribute access: item.level, item.message, item.numbers
    """
    def __new__(cls, level: str, message: str, numbers: Dict[str, Any]):
        return super().__new__(cls, (level, message, numbers))

    def __init__(self, level: str, message: str, numbers: Dict[str, Any]):
        self.level = level          # "red", "amber", "green"
        self.message = message
        self.numbers = numbers

    def __getitem__(self, item):
        if isinstance(item, str):
            return getattr(self, item, None)
        return super().__getitem__(item)


def waste_checks(bills: Any, answers: Any, normal: Optional[float] = None) -> List[WasteCheckResult]:
    """
    Evaluate bill history alongside submitted answers.

    Checks:
      1. Vacation test: away 5+ days but bill did not drop -> 'something stays on'.
      2. Rising baseline floor: if >= 6 bills and lowest-month floor rose.
      3. Unexplained units: part of the jump not covered by answers.
      4. Estimated bill present: recommend asking BESCOM for a real reading (1912).
      5. Near the 200 line: warn about Gruha Jyothi threshold.

    Returns:
      list of (level, message, numbers)
    """
    # Safe bill extraction
    cleaned_bills = []
    if isinstance(bills, list):
        for b in bills:
            if isinstance(b, dict):
                cleaned_bills.append({
                    "month": b.get("month", ""),
                    "units": max(float(b.get("units", b.get("kwh", 0.0)) or 0.0), 0.0),
                    "days": max(int(b.get("days", b.get("billing_days", 30)) or 30), 1),
                    "away": max(int(b.get("away", b.get("away_days", 0)) or 0), 0),
                    "estimated": bool(b.get("estimated", False)),
                    "fuel_per_unit": float(b.get("fuel_per_unit", b.get("fuel", 0.0)) or 0.0),
                    "free_units": b.get("free_units", b.get("free")),
                    "load_kw": float(b.get("load_kw", b.get("kw", 2.0)) or 2.0)
                })
    elif isinstance(bills, dict) and "cur" in bills:
        if bills.get("prev"):
            cleaned_bills.append(bills["prev"])
        if bills.get("cur"):
            cleaned_bills.append(bills["cur"])

    ans = normalize_answers(answers)
    cur = cleaned_bills[-1] if cleaned_bills else None
    prev = cleaned_bills[-2] if len(cleaned_bills) >= 2 else None

    # Calculate baseline normal use
    if normal is None or normal <= 0:
        if "normal_use" in globals() and callable(globals()["normal_use"]):
            normal = normal_use(cleaned_bills)
        elif prev:
            dp = prev["days"]
            pa = prev["away"]
            eff_prev = (dp - pa) + AWAY_SHARE * pa
            normal = prev["units"] / max(eff_prev, 1.0)
        elif cur:
            normal = cur["units"] / max(cur["days"], 1.0)
        else:
            normal = 5.0

    eff_rate = RATE * (1 + TAX)
    out: List[WasteCheckResult] = []

    vacation_days = max(ans["vacation_days"], cur["away"] if cur else 0)

    # 1. Vacation test: away 5+ days but bill did not drop
    if vacation_days >= 5 and cur:
        home_days = max(cur["days"] - vacation_days, 0)
        home_units = normal * home_days
        expected_away_units = normal * AWAY_SHARE * vacation_days
        expected_total = home_units + expected_away_units

        if cur["units"] > 1.25 * expected_total and not (prev and prev.get("estimated")):
            excess_units = max(cur["units"] - expected_total, 0.0)
            excess_rs = excess_units * eff_rate
            daily_away = (cur["units"] - home_units) / max(vacation_days, 1)

            culprits = "water motor running, geyser left switched on, old fridge compressor, or inverter standby"
            msg = (
                f"Vacation test FAILED: You were away {vacation_days} days, but the home used about "
                f"{daily_away:.1f} units/day. That is ~{excess_units:.0f} wasted units ({rupees(excess_rs)}). "
                f"Something stays ON when nobody is home: check {culprits}."
            )
            out.append(WasteCheckResult(
                level="red",
                message=msg,
                numbers={
                    "days": vacation_days,
                    "per_day": round(daily_away, 1),
                    "units": round(excess_units),
                    "rupees": round(excess_rs),
                    "culprits": culprits
                }
            ))
        else:
            msg = f"Vacation test PASSED: While away for {vacation_days} days, your standby idle load stayed low (~{expected_away_units:.0f} units total). Good habit!"
            out.append(WasteCheckResult(
                level="green",
                message=msg,
                numbers={"days": vacation_days, "expected_standby_units": round(expected_away_units)}
            ))

    # 2. Rising baseline floor (if >= 6 bills)
    if len(cleaned_bills) >= 6:
        daily_rates = [b["units"] / max(b["days"], 1) for b in cleaned_bills]
        half = len(daily_rates) // 2
        old_floor = min(daily_rates[:half])
        new_floor = min(daily_rates[half:])

        if new_floor > old_floor * 1.25 and (new_floor - old_floor) >= 0.8:
            rise_pct = ((new_floor - old_floor) / max(old_floor, 0.1)) * 100.0
            excess_floor_units = (new_floor - old_floor) * 30.0
            msg = (
                f"Rising baseline floor alert: Your lowest-month floor rose by {rise_pct:.0f}% "
                f"(from {old_floor:.1f} to {new_floor:.1f} units/day). "
                f"That adds ~{excess_floor_units:.0f} always-on units ({rupees(excess_floor_units * eff_rate)}) every month."
            )
            out.append(WasteCheckResult(
                level="amber",
                message=msg,
                numbers={
                    "old_floor": round(old_floor, 1),
                    "new_floor": round(new_floor, 1),
                    "rise_pct": round(rise_pct),
                    "monthly_units": round(excess_floor_units),
                    "monthly_rupees": round(excess_floor_units * eff_rate)
                }
            ))

    # 3. Unexplained units: part of the jump not covered by answers
    if cur and prev:
        unit_jump = cur["units"] - prev["units"]
        if unit_jump > 20:
            home_days = max(cur["days"] - vacation_days, 0)
            explained_est = 0.0
            if ans["guests_days"] > 0 and ans["guests_people"] > 0:
                explained_est += 1.2 * ans["guests_people"] * min(ans["guests_days"], home_days)
            if ans["hot_ac"]:
                explained_est += 3.0 * home_days * 0.5
            if ans["geyser"]:
                explained_est += 1.0 * home_days * 0.5
            if ans["home_more"]:
                explained_est += 1.5 * home_days * 0.6
            if ans["pump"]:
                explained_est += 0.4 * home_days
            if ans["new_items"]:
                explained_est += len(ans["new_items"]) * 1.5 * home_days * 0.5

            unexplained = unit_jump - explained_est
            if unexplained >= 15:
                u_rs = unexplained * eff_rate
                culprits = "water motor overflow, geyser left on standby, aging inverter batteries, or old fridge door seal"
                msg = (
                    f"Unexplained units: About {unexplained:.0f} units (~{rupees(u_rs)}) are not covered by your answers. "
                    f"Check these suspects: {culprits}."
                )
                out.append(WasteCheckResult(
                    level="amber",
                    message=msg,
                    numbers={
                        "units": round(unexplained),
                        "rupees": round(u_rs),
                        "culprits": culprits
                    }
                ))

    # 4. Estimated bill present
    has_estimate = any(b.get("estimated") for b in cleaned_bills[-2:])
    if has_estimate:
        msg = "Estimated bill present: Meter was not read; BESCOM billed an average. Request a real reading (call helpline 1912 or use Mithra app) to avoid catch-up spikes."
        out.append(WasteCheckResult(
            level="amber",
            message=msg,
            numbers={"helpline": "1912"}
        ))

    # 5. Near the 200 line (Gruha Jyothi)
    if cur:
        c_units = cur["units"]
        if c_units > GJ_CAP:
            over = c_units - GJ_CAP
            msg = f"Crossed the 200-unit line ({c_units:.0f} units, +{over:.0f} over). Gruha Jyothi stopped for this month; full bill is payable."
            out.append(WasteCheckResult(
                level="red",
                message=msg,
                numbers={"units": round(c_units), "cap": GJ_CAP, "over": round(over)}
            ))
        elif (GJ_CAP - 15) <= c_units <= GJ_CAP:
            buffer = GJ_CAP - c_units
            msg = f"Near the 200 line: At {c_units:.0f} units, you are only {buffer:.0f} units from losing the entire Gruha Jyothi subsidy."
            out.append(WasteCheckResult(
                level="amber",
                message=msg,
                numbers={"units": round(c_units), "cap": GJ_CAP, "buffer": round(buffer)}
            ))

    if not out:
        out.append(WasteCheckResult(
            level="green",
            message="No waste detected: Your electricity consumption looks normal and aligns with your answers.",
            numbers={"status": "normal"}
        ))

    return out


# -----------------------------------------------------------------------------
# 3) tips(answers, bills) -> ranked list of (message, units_saved_range, rupees_range, cost, who)
# -----------------------------------------------------------------------------
class SavingTipResult(tuple):
    """
    5-tuple (message, units_saved_range, rupees_range, cost, who) supporting:
      - 5-tuple unpacking: message, units_range, rs_range, cost, who = tip
      - 2-tuple unpacking (legacy): message, cost = tip
      - attribute access: tip.message, tip.rupees_range, tip.cost, etc.
    """
    def __new__(cls, message: str, units_saved_range: str, rupees_range: str,
                cost: str, who: str, rank_rupees: float = 0.0):
        return super().__new__(cls, (message, units_saved_range, rupees_range, cost, who))

    def __init__(self, message: str, units_saved_range: str, rupees_range: str,
                 cost: str, who: str, rank_rupees: float = 0.0):
        self.message = message
        self.units_saved_range = units_saved_range
        self.rupees_range = rupees_range
        self.cost = cost
        self.who = who
        self.rank_rupees = rank_rupees

    def __getitem__(self, item):
        if isinstance(item, str):
            return getattr(self, item, None)
        return super().__getitem__(item)


def tips(answers: Any, bills: Any) -> List[SavingTipResult]:
    """
    Return ranked list of saving recommendations.

    Rules:
      - Tips come from ANSWERS only (no appliance inventory).
      - Ranked by estimated rupees saved.
      - Every number is a RANGE with an '(estimate)' tag.
      - Includes a Gruha Jyothi tip when over 200.

    Returns:
      ranked list of (message, units_saved_range, rupees_range, cost, who)
    """
    ans = normalize_answers(answers)

    cur = None
    if isinstance(bills, list) and len(bills) > 0:
        b = bills[-1]
        if isinstance(b, dict):
            cur = b
    elif isinstance(bills, dict) and "cur" in bills:
        cur = bills["cur"]

    tip_list: List[SavingTipResult] = []

    # 1. Gruha Jyothi Tip when over 200 units
    if cur and cur.get("units", 0.0) > GJ_CAP:
        over = cur["units"] - GJ_CAP
        tip_list.append(SavingTipResult(
            message=f"Reduce usage below 200 units (currently {over:.0f} units over) to restore your Gruha Jyothi zero-bill subsidy.",
            units_saved_range=f"{over:.0f} to {over + 10:.0f} units (estimate)",
            rupees_range="₹1,100 to ₹1,450 / month (estimate)",
            cost="Free",
            who="Gruha Jyothi households",
            rank_rupees=1300.0
        ))

    # 2. Hot weather / AC
    if ans["hot_ac"] or ("AC" in ans["new_items"]):
        tip_list.append(SavingTipResult(
            message="Set AC temperature to 24°C or 25°C instead of 18°C–21°C. Each degree saves ~6% electricity.",
            units_saved_range="45 to 65 units / month (estimate)",
            rupees_range="₹280 to ₹420 / month (estimate)",
            cost="Free",
            who="AC users",
            rank_rupees=350.0
        ))
        tip_list.append(SavingTipResult(
            message="Clean AC mesh air filters every 15 days to reduce compressor workload.",
            units_saved_range="20 to 30 units / month (estimate)",
            rupees_range="₹120 to ₹190 / month (estimate)",
            cost="Free",
            who="AC users",
            rank_rupees=160.0
        ))

    # 3. Cold/rainy weather / Geyser
    if ans["geyser"] or ("Geyser" in ans["new_items"]):
        tip_list.append(SavingTipResult(
            message="Switch off the geyser wall switch right after bathing; avoid leaving it on to eliminate standing reheat losses.",
            units_saved_range="30 to 45 units / month (estimate)",
            rupees_range="₹190 to ₹290 / month (estimate)",
            cost="Free to ₹350 (timer)",
            who="Geyser users",
            rank_rupees=240.0
        ))

    # 4. Water motor / Pump
    if ans["pump"]:
        tip_list.append(SavingTipResult(
            message="Install an automatic water-level controller on the overhead tank to eliminate overflows.",
            units_saved_range="20 to 35 units / month (estimate)",
            rupees_range="₹130 to ₹230 / month (estimate)",
            cost="₹400 to ₹800",
            who="Water motor users",
            rank_rupees=180.0
        ))

    # 5. Vacation / Away days
    if ans["vacation_days"] >= 3:
        tip_list.append(SavingTipResult(
            message="Before leaving home: turn off geyser, water motor, and TV/Wi-Fi sub-switches at the distribution board.",
            units_saved_range="15 to 30 units / trip (estimate)",
            rupees_range="₹95 to ₹190 / trip (estimate)",
            cost="Free",
            who="Travelers",
            rank_rupees=145.0
        ))

    # 6. Guests staying over
    if ans["guests_days"] > 0 and ans["guests_people"] > 0:
        tip_list.append(SavingTipResult(
            message="Batch laundry into full washing loads and take consecutive hot showers to reuse residual geyser tank heat.",
            units_saved_range="15 to 25 units (estimate)",
            rupees_range="₹95 to ₹160 (estimate)",
            cost="Free",
            who="Households with guests",
            rank_rupees=130.0
        ))

    # 7. Inverter charging / Power cuts
    if ans["power_cuts"]:
        tip_list.append(SavingTipResult(
            message="Check inverter battery electrolyte levels; dry battery cells draw heavy continuous trickle charge non-stop.",
            units_saved_range="25 to 45 units / month (estimate)",
            rupees_range="₹160 to ₹290 / month (estimate)",
            cost="₹50 (distilled water)",
            who="Inverter owners",
            rank_rupees=220.0
        ))

    # 8. Festival lights
    if ans["festival_lights"]:
        tip_list.append(SavingTipResult(
            message="Replace incandescent serial bulb sets with 5W LED strings connected to a 4-hour automatic timer plug.",
            units_saved_range="15 to 25 units / season (estimate)",
            rupees_range="₹95 to ₹160 (estimate)",
            cost="₹200 to ₹400",
            who="Festival lighting users",
            rank_rupees=125.0
        ))

    # 9. EV / E-scooter charging
    if "EV / e-scooter" in ans["new_items"] or "EV/e-scooter" in ans["new_items"]:
        tip_list.append(SavingTipResult(
            message="Unplug e-scooter charger once battery reaches 85% to eliminate idle transformer drain.",
            units_saved_range="10 to 20 units / month (estimate)",
            rupees_range="₹65 to ₹130 / month (estimate)",
            cost="Free",
            who="EV owners",
            rank_rupees=95.0
        ))

    # 10. General baseline / standby power
    tip_list.append(SavingTipResult(
        message="Turn off TV set-top boxes and microwave displays at the wall socket when not in use overnight.",
        units_saved_range="10 to 18 units / month (estimate)",
        rupees_range="₹65 to ₹115 / month (estimate)",
        cost="Free",
        who="Everyone",
        rank_rupees=90.0
    ))

    # Rank by rupees saved descending
    tip_list.sort(key=lambda t: -t.rank_rupees)
    return tip_list
