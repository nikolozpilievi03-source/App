"""
Database layer with dual support:

- PostgreSQL in production  -> used automatically when the DATABASE_URL
  environment variable is set (e.g. on Render, pointing to Neon).
  Data survives every deploy and restart.

- SQLite for local development -> used when DATABASE_URL is not set
  (your Windows PC with voice reminders + addiction monitor).

All queries are written once with '?' placeholders and converted
to '%s' automatically for Postgres.
"""

import os
import sqlite3
from datetime import date, time
from models import Routine

DB_NAME = "discipline.db"
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    print("🐘 Database: PostgreSQL (persistent cloud storage)")
else:
    print("📁 Database: SQLite (local development)")


# ============================================================
# CONNECTION HELPERS
# ============================================================

def get_connection():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def _q(query: str) -> str:
    """Convert SQLite-style '?' placeholders to Postgres '%s'."""
    return query.replace("?", "%s") if USE_POSTGRES else query


# ============================================================
# SCHEMA
# ============================================================

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    id_column = "SERIAL PRIMARY KEY" if USE_POSTGRES else "INTEGER PRIMARY KEY"

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS routines (
        id {id_column},
        title TEXT,
        routine_date TEXT,
        routine_time TEXT,
        status TEXT,
        reminder_sent INTEGER,
        personality TEXT,
        streak INTEGER,
        failures INTEGER,
        user_id TEXT DEFAULT 'default'
    )
    """)

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS block_logs (
        id {id_column},
        user_id TEXT,
        category TEXT NOT NULL,
        url TEXT,
        title TEXT,
        timestamp TEXT NOT NULL,
        audio_type TEXT
    )
    """)

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS block_stats (
        id {id_column},
        user_id TEXT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        blocks_count INTEGER DEFAULT 0,
        UNIQUE(user_id, date, category)
    )
    """)

    # SQLite migration: add user_id to old local databases if missing
    if not USE_POSTGRES:
        try:
            cursor.execute("ALTER TABLE routines ADD COLUMN user_id TEXT DEFAULT 'default'")
            print("✅ Added user_id column to routines table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                print(f"⚠️  Migration note: {e}")

    conn.commit()
    conn.close()
    print("✅ Database tables ready")


# ============================================================
# ROUTINES
# ============================================================

def insert_routine(routine: Routine):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(_q("""
        INSERT INTO routines (
            title, routine_date, routine_time, status,
            reminder_sent, personality, streak, failures, user_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """), (
        routine.title,
        routine.routine_date.isoformat(),
        routine.routine_time.strftime("%H:%M"),
        routine.status,
        int(routine.reminder_sent),
        routine.personality,
        routine.streak,
        routine.failures,
        routine.user_id if hasattr(routine, 'user_id') else 'default'
    ))
    conn.commit()
    conn.close()


def get_all_routines(user_id: str = None):
    conn = get_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute(_q(
            "SELECT id, title, routine_date, routine_time, status, "
            "reminder_sent, personality, streak, failures, user_id "
            "FROM routines WHERE user_id = ?"
        ), (user_id,))
    else:
        cursor.execute(
            "SELECT id, title, routine_date, routine_time, status, "
            "reminder_sent, personality, streak, failures, user_id "
            "FROM routines"
        )

    rows = cursor.fetchall()
    conn.close()

    routines = []
    for row in rows:
        routines.append(
            Routine(
                id=row[0],
                title=row[1],
                routine_date=date.fromisoformat(row[2]),
                routine_time=time.fromisoformat(row[3]),
                status=row[4],
                reminder_sent=bool(row[5]),
                personality=row[6],
                streak=row[7],
                failures=row[8],
                user_id=row[9] if row[9] else "default"
            )
        )
    return routines


def update_routine(routine: Routine):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(_q("""
        UPDATE routines
        SET status = ?, reminder_sent = ?, streak = ?, failures = ?
        WHERE id = ?
    """), (
        routine.status,
        int(routine.reminder_sent),
        routine.streak,
        routine.failures,
        routine.id
    ))
    conn.commit()
    conn.close()


def update_routine_details(routine_id: int, title=None, routine_date=None,
                           routine_time=None, personality=None):
    """Update the editable fields of a routine. Returns True if a row changed."""
    fields = []
    values = []
    if title is not None:
        fields.append("title = ?")
        values.append(title)
    if routine_date is not None:
        fields.append("routine_date = ?")
        values.append(routine_date)
    if routine_time is not None:
        fields.append("routine_time = ?")
        values.append(routine_time)
    if personality is not None:
        fields.append("personality = ?")
        values.append(personality)

    if not fields:
        return False

    values.append(routine_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(_q(f"UPDATE routines SET {', '.join(fields)} WHERE id = ?"), values)
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed


def delete_routine_by_id(routine_id: int):
    """Delete a routine. Returns True if a row was deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(_q("DELETE FROM routines WHERE id = ?"), (routine_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ============================================================
# ADDICTION MONITORING (cloud logging from mobile)
# ============================================================

def log_block(user_id: str, category: str, url: str = "",
              title: str = "", audio_type: str = "warning",
              timestamp: str = None):
    """Log a block attempt and bump the daily counter."""
    from datetime import datetime
    ts = timestamp or datetime.now().isoformat()
    today = ts[:10]  # YYYY-MM-DD

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(_q("""
        INSERT INTO block_logs (user_id, category, url, title, timestamp, audio_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """), (user_id, category, url, title, ts, audio_type))

    if USE_POSTGRES:
        cursor.execute("""
            INSERT INTO block_stats (user_id, date, category, blocks_count)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT (user_id, date, category)
            DO UPDATE SET blocks_count = block_stats.blocks_count + 1
        """, (user_id, today, category))
    else:
        cursor.execute("""
            INSERT INTO block_stats (user_id, date, category, blocks_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(user_id, date, category)
            DO UPDATE SET blocks_count = blocks_count + 1
        """, (user_id, today, category))

    conn.commit()
    conn.close()


def get_block_stats_rows(days: int = 7, user_id: str = None):
    """Return (date, category, blocks_count) rows for the last N days."""
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        if user_id:
            cursor.execute("""
                SELECT date, category, blocks_count FROM block_stats
                WHERE date >= (CURRENT_DATE - %s * INTERVAL '1 day')::date::text
                  AND user_id = %s
                ORDER BY date DESC
            """, (days, user_id))
        else:
            cursor.execute("""
                SELECT date, category, blocks_count FROM block_stats
                WHERE date >= (CURRENT_DATE - %s * INTERVAL '1 day')::date::text
                ORDER BY date DESC
            """, (days,))
    else:
        if user_id:
            cursor.execute("""
                SELECT date, category, blocks_count FROM block_stats
                WHERE date >= date('now', '-' || ? || ' days')
                  AND user_id = ?
                ORDER BY date DESC
            """, (days, user_id))
        else:
            cursor.execute("""
                SELECT date, category, blocks_count FROM block_stats
                WHERE date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC
            """, (days,))

    results = cursor.fetchall()
    conn.close()
    return results