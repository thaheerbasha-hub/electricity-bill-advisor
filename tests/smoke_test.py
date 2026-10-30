"""
smoke_test.py · Opens every page for several family profiles and fails if any page crashes.

Run from the project folder:
    python tests/smoke_test.py

Uses a throwaway database, so the real power_coach.db is never touched.
"""

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import db  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

db.DB_PATH = os.path.join(tempfile.mkdtemp(), "smoke.db")
db.init_db()

PAGES = [
    "pages/2_Home.py",
    "pages/3_My_Bills.py",
    "pages/4_What_Changed.py",
    "pages/5_Results.py",
    "pages/6_Forecast.py",
    "pages/7_About_Karnataka.py",
    "pages/8_Settings.py",
]

# name -> list of (month, units, days, estimated, fuel_per_unit, free_units, load_kw)
PROFILES = {
    "fuel Rs 4/unit": [("Aug 2026", 140, 30, 0, 4.0, 150, 2.0), ("Sep 2026", 160, 30, 0, 4.0, 150, 2.0)],
    "150 units/day": [("Aug 2026", 4400, 30, 0, 0.5, None, 10.0), ("Sep 2026", 4500, 30, 0, 0.5, None, 10.0)],
    "not in Gruha Jyothi": [("Aug 2026", 140, 30, 0, 0.5, None, 2.0), ("Sep 2026", 150, 30, 0, 0.5, None, 2.0)],
    "0 free units": [("Aug 2026", 140, 30, 0, 0.5, 0, 2.0), ("Sep 2026", 150, 30, 0, 0.5, 0, 2.0)],
    "bill stays Rs 0": [("Aug 2026", 90, 30, 0, 0.5, 150, 2.0), ("Sep 2026", 100, 30, 0, 0.5, 150, 2.0)],
    "lost Gruha Jyothi": [("Aug 2026", 140, 30, 0, 0.5, 150, 2.0), ("Sep 2026", 210, 30, 0, 0.5, 150, 2.0)],
    "estimated bill": [("Aug 2026", 140, 30, 1, 0.5, 150, 2.0), ("Sep 2026", 190, 31, 0, 0.5, 150, 2.0)],
    "one bill only": [("Sep 2026", 150, 30, 0, 0.5, 150, 2.0)],
    "across years, mixed formats": [("Sep 2026", 160, 30, 0, 0.5, 150, 2.0), ("Nov 2025", 120, 30, 0, 0.5, 150, 2.0),
                                    ("2026-08", 150, 31, 0, 0.5, 150, 2.0)],
    "no bills": [],
}

ANSWERS = {"away_days": 5, "guests_people": 2, "guests_days": 10, "heat": True, "new_items": ["AC"]}


def run(page, user, lang, answers):
    at = AppTest.from_file(os.path.join(ROOT, page), default_timeout=60)
    at.session_state["user"] = user
    at.session_state["lang"] = lang
    if answers is not None:
        at.session_state["answers"] = answers
    at.run()
    return at.exception


def main():
    failures = []
    for i, (name, bills) in enumerate(PROFILES.items()):
        uid = db.add_user(f"Test {i}", f"90000000{i:02d}", "1234")
        assert uid, f"could not create user for {name}"
        for b in bills:
            db.add_bill(uid, *b)
        user = {"id": uid, "name": f"Test {i}", "phone": f"90000000{i:02d}"}
        for page in PAGES:
            for lang in ("en", "kn"):
                for answers in (None, ANSWERS):
                    exc = run(page, user, lang, answers)
                    if exc:
                        failures.append(f"{name} | {page} | {lang} | answers={answers is not None}: {exc[0].message}")

    # Bills must come back oldest-first by real month, not alphabetically.
    uid = db.add_user("Order", "9000000999", "1234")
    for m in ("Sep 2026", "Nov 2025", "Aug 2026"):
        db.add_bill(uid, m, 100, 30, 0, 0.5, 150, 2.0)
    order = [b["month"] for b in db.get_bills(uid)]
    if order != ["Nov 2025", "Aug 2026", "Sep 2026"]:
        failures.append(f"bill order wrong: {order}")

    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print(f"OK: {len(PROFILES)} profiles x {len(PAGES)} pages x 2 languages x 2 answer sets, no crashes.")


if __name__ == "__main__":
    main()
