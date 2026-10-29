"""
db.py · SQLite database for Power Bill Coach
Tables:
  - users (id, name, phone, pin_hash)
  - bills (id, user_id, month, units, days, estimated, fuel_per_unit, free_units, load_kw)

Shared helpers:
  - init_db()
  - add_user(name, phone, pin)
  - check_login(phone, pin)
  - add_bill(user_id, month, units, days, estimated, fuel_per_unit, free_units, load_kw)
  - update_bill(bill_id, user_id, month, units, days, estimated, fuel_per_unit, free_units, load_kw)
  - delete_bill(bill_id, user_id=None)
  - get_bills(user_id)
"""

import hashlib
import math
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "power_coach.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_pin(pin: str) -> str:
    salt = "karnataka_bescom_salt_2026"
    return hashlib.sha256(f"{salt}_{pin}".encode("utf-8")).hexdigest()


def _num(x, default=0.0):
    if x is None:
        return default
    if isinstance(x, str):
        x = x.strip()
        if not x:
            return default
    try:
        val = float(x)
        if math.isnan(val) or math.isinf(val):
            return default
        return val
    except (ValueError, TypeError):
        return default


def init_db():
    conn = get_conn()
    try:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            units REAL NOT NULL,
            days INTEGER NOT NULL,
            estimated INTEGER NOT NULL DEFAULT 0,
            fuel_per_unit REAL NOT NULL DEFAULT 0.0,
            free_units REAL,
            load_kw REAL NOT NULL DEFAULT 2.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        conn.commit()

        # Check for column rename migration
        cur.execute("PRAGMA table_info(bills);")
        cols = [r["name"] if isinstance(r, sqlite3.Row) else r[1] for r in cur.fetchall()]
        if "fuel_rs" in cols:
            cur.execute("ALTER TABLE bills RENAME COLUMN fuel_rs TO fuel_per_unit;")
            conn.commit()

        seed_demo_user(conn)
    finally:
        conn.close()


def seed_demo_user(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE phone = ?", ("9876543210",))
    demo = cur.fetchone()
    if not demo:
        pin_h = hash_pin("1234")
        cur.execute(
            "INSERT INTO users (name, phone, pin_hash) VALUES (?, ?, ?)",
            ("Ramesh Kumar (Demo)", "9876543210", pin_h)
        )
        user_id = cur.lastrowid
    else:
        user_id = demo["id"] if isinstance(demo, sqlite3.Row) else demo[0]

    cur.execute("SELECT id, month FROM bills WHERE user_id = ?", (user_id,))
    existing_bills = cur.fetchall()

    def is_old_month(m):
        if not m:
            return True
        s = str(m).strip()
        if len(s) == 7 and s[:4].isdigit() and s[4] == '-' and s[5:].isdigit():
            return False
        return True

    needs_reseed = (len(existing_bills) == 0) or any(
        is_old_month(b["month"] if isinstance(b, sqlite3.Row) else b[1]) for b in existing_bills
    )

    if needs_reseed:
        cur.execute("DELETE FROM bills WHERE user_id = ?", (user_id,))
        sample_bills = [
            ("2026-05", 152.0, 30, 0, 0.35, 150.0, 2.0),
            ("2026-06", 160.0, 31, 0, 0.35, 150.0, 2.0),
            ("2026-07", 148.0, 30, 0, 0.35, 150.0, 2.0),
            ("2026-08", 155.0, 31, 0, 0.37, 150.0, 2.0),
            ("2026-09", 168.0, 30, 0, 0.37, 150.0, 2.0),
            ("2026-10", 206.0, 31, 0, 0.37, 150.0, 2.0),
        ]
        for b in sample_bills:
            cur.execute("""
            INSERT INTO bills (user_id, month, units, days, estimated, fuel_per_unit, free_units, load_kw)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, b[0], b[1], b[2], b[3], b[4], b[5], b[6]))
        conn.commit()


def add_user(name: str, phone: str, pin: str):
    name = (name or "").strip()
    phone = (phone or "").strip()
    pin = (pin or "").strip()
    if len(phone) < 10 or not pin or not name:
        return None
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, phone, pin_hash) VALUES (?, ?, ?)",
            (name, phone, hash_pin(pin))
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    except Exception:
        return None
    finally:
        if conn is not None:
            conn.close()


def check_login(phone: str, pin: str):
    phone = (phone or "").strip()
    pin = (pin or "").strip()
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, phone, pin_hash FROM users WHERE phone = ?",
            (phone,)
        )
        row = cur.fetchone()
        if row and row["pin_hash"] == hash_pin(pin):
            return {"id": row["id"], "name": row["name"], "phone": row["phone"]}
        return None
    finally:
        conn.close()


def add_bill(user_id: int, month: str, units, days, estimated, fuel_per_unit, free_units, load_kw):
    u = max(0.0, _num(units, 0.0))
    d = max(1, int(round(_num(days, 1.0))))
    est = 1 if estimated else 0
    f = max(0.0, _num(fuel_per_unit, 0.0))
    if free_units is None or (isinstance(free_units, str) and not free_units.strip()):
        free_u = None
    else:
        val = _num(free_units, None)
        free_u = max(0.0, val) if val is not None else None
    kw = max(0.0, _num(load_kw, 0.0))
    m = str(month).strip() if month else ""

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO bills (user_id, month, units, days, estimated, fuel_per_unit, free_units, load_kw)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, m, u, d, est, f, free_u, kw))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_bill(bill_id: int, user_id: int, month: str, units, days, estimated, fuel_per_unit, free_units, load_kw):
    u = max(0.0, _num(units, 0.0))
    d = max(1, int(round(_num(days, 1.0))))
    est = 1 if estimated else 0
    f = max(0.0, _num(fuel_per_unit, 0.0))
    if free_units is None or (isinstance(free_units, str) and not free_units.strip()):
        free_u = None
    else:
        val = _num(free_units, None)
        free_u = max(0.0, val) if val is not None else None
    kw = max(0.0, _num(load_kw, 0.0))
    m = str(month).strip() if month else ""

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
        UPDATE bills
        SET month = ?, units = ?, days = ?, estimated = ?, fuel_per_unit = ?, free_units = ?, load_kw = ?
        WHERE id = ? AND user_id = ?
        """, (m, u, d, est, f, free_u, kw, bill_id, user_id))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def delete_bill(bill_id: int, user_id: int = None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        if user_id is not None:
            cur.execute("DELETE FROM bills WHERE id = ? AND user_id = ?", (bill_id, user_id))
        else:
            cur.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


_MONTH_FORMATS = ("%Y-%m", "%Y-%m-%d", "%b %Y", "%B %Y", "%b-%Y", "%b %y", "%m/%Y", "%m-%Y")


def _parse_month(label):
    """'Sep 2026' / '2026-09' -> (2026, 9); None if it cannot be read."""
    text = " ".join(str(label or "").replace(",", " ").split())
    for fmt in _MONTH_FORMATS:
        try:
            dt = datetime.strptime(text, fmt)
            return (dt.year, dt.month)
        except ValueError:
            continue
    return None


def _sort_by_month(rows):
    """Oldest bill first by real calendar month (text sort puts 'Nov 2025' after 'Aug 2026').
    Rows come in id order; a month that cannot be read keeps the slot of the bill entered before it."""
    last = (0, 0)
    keyed = []
    for i, r in enumerate(rows):
        ym = _parse_month(r.get("month"))
        if ym:
            last = ym
        keyed.append((ym or last, i, r))
    keyed.sort(key=lambda t: (t[0], t[1]))
    return [r for _, _, r in keyed]


def get_bills(user_id: int):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT id, month, units, days, estimated, fuel_per_unit, free_units, load_kw
        FROM bills
        WHERE user_id = ?
        ORDER BY id ASC
        """, (user_id,))
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            d["units"] = float(d["units"])
            d["days"] = int(d["days"])
            d["estimated"] = bool(d["estimated"])
            d["fuel_per_unit"] = float(d["fuel_per_unit"])
            d["fuel_rs"] = d["fuel_per_unit"]
            d["free_units"] = float(d["free_units"]) if d["free_units"] is not None else None
            d["load_kw"] = float(d["load_kw"])
            rows.append(d)
        return _sort_by_month(rows)
    finally:
        conn.close()


# Initialize table on import
init_db()
