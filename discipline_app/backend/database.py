import sqlite3
from models import Routine
from datetime import date, time

DB_NAME = "discipline.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routines (
        id INTEGER PRIMARY KEY,
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
    conn.commit()
    conn.close()

def insert_routine(routine: Routine):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO routines (
            title,
            routine_date,
            routine_time,
            status,
            reminder_sent,
            personality,
            streak,
            failures,
            user_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        routine.title,
        routine.routine_date.isoformat(),
        routine.routine_time.strftime("%H:%M"),
        routine.status,
        int(routine.reminder_sent),
        routine.personality,
        routine.streak,
        routine.failures,
        routine.user_id
    ))
    conn.commit()
    conn.close()

def get_all_routines(user_id: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute("SELECT * FROM routines WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT * FROM routines")
    
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
                user_id=row[9] if len(row) > 9 else "default"
            )
        )
    return routines

def update_routine(routine: Routine):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE routines
        SET status = ?, reminder_sent = ?, streak = ?, failures = ?
        WHERE id = ?
    """, (
        routine.status,
        int(routine.reminder_sent),
        routine.streak,
        routine.failures,
        routine.id
    ))
    conn.commit()
    conn.close()