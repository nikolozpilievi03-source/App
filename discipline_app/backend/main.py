from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from database import init_db, insert_routine
from models import Routine
from logic import evaluate_routine_status, background_time_watcher
from database import get_all_routines, update_routine
import threading
import uvicorn
import sqlite3
from datetime import datetime
import platform

app = FastAPI(title="Discipline App")

# Add CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("🚀 FastAPI startup event triggered")

    init_db()
    init_addiction_db()

    watcher = threading.Thread(
        target=background_time_watcher,
        daemon=True
    )
    watcher.start()

    if ADDICTION_MONITOR_AVAILABLE:
        monitor = threading.Thread(
            target=addiction_monitor_loop,
            daemon=True
        )
        monitor.start()

# Check if running on Windows (for local development with addiction monitor)
IS_WINDOWS = platform.system() == 'Windows'

# Only import Windows-specific code if on Windows
if IS_WINDOWS:
    try:
        from addiction_monitor import addiction_monitor_loop, init_addiction_db, get_block_stats
        ADDICTION_MONITOR_AVAILABLE = True
    except ImportError:
        print("⚠️  Addiction monitor not available (Windows-only feature)")
        ADDICTION_MONITOR_AVAILABLE = False
else:
    ADDICTION_MONITOR_AVAILABLE = False
    # Create dummy functions for cloud deployment
    def init_addiction_db():
        """Initialize addiction database tables (cloud version)"""
        conn = sqlite3.connect('discipline.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS block_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                category TEXT NOT NULL,
                url TEXT,
                title TEXT,
                timestamp TEXT NOT NULL,
                audio_type TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS block_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                blocks_count INTEGER DEFAULT 0,
                UNIQUE(user_id, date, category)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_block_stats(days=7):
        """Get blocking statistics (cloud version)"""
        conn = sqlite3.connect('discipline.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, category, blocks_count
            FROM block_stats
            WHERE date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        """, (days,))
        
        results = cursor.fetchall()
        conn.close()
        return results

@app.get("/")
def root():
    return {
        "status": "Backend running successfully",
        "platform": platform.system(),
        "addiction_monitor": "active" if ADDICTION_MONITOR_AVAILABLE else "mobile-only"
    }

@app.post("/routines")
def create_routines(routines: List[Routine]):
    for routine in routines:
        insert_routine(routine)
    return {"created": len(routines)}

@app.get("/routines")
def list_routines():
    routines = get_all_routines()
    updated = []
    for routine in routines:
        updated_routine = evaluate_routine_status(routine)
        update_routine(updated_routine)
        updated.append(updated_routine)
    return updated

@app.post("/routines/{routine_id}/complete")
def complete_routine(routine_id: int):
    routines = get_all_routines()
    routine = next((r for r in routines if r.id == routine_id), None)
    if not routine:
        return {"error": "Routine not found"}
    if routine.status == "missed":
        return {"error": "Routine already missed"}
    routine.status = "done"
    routine.streak += 1
    update_routine(routine)
    return routine

@app.get("/addiction-stats")
def get_addiction_stats():
    """Get addiction blocking statistics"""
    stats = get_block_stats(7)
    
    # Format for API response
    by_category = {}
    by_date = {}
    
    for date, category, count in stats:
        if category not in by_category:
            by_category[category] = 0
        by_category[category] += count
        
        if date not in by_date:
            by_date[date] = {}
        by_date[date][category] = count
    
    return {
        "total_by_category": by_category,
        "by_date": by_date
    }

@app.post("/log-block")
def log_block_from_mobile(
    user_id: str = "default",
    category: str = None,
    url: str = "",
    title: str = "",
    audio_type: str = "warning"
):
    """Log a block attempt from mobile app"""
    try:
        conn = sqlite3.connect('discipline.db')
        cursor = conn.cursor()
        
        # Log the block
        cursor.execute("""
            INSERT INTO block_logs (user_id, category, url, title, timestamp, audio_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, category, url, title, datetime.now().isoformat(), audio_type))
        
        # Update stats
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            INSERT INTO block_stats (user_id, date, category, blocks_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(user_id, date, category)
            DO UPDATE SET blocks_count = blocks_count + 1
        """, (user_id, today, category))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Block logged"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/routines/{routine_id}")
def delete_routine(routine_id: int):
    """Delete a routine by ID"""
    conn = sqlite3.connect('discipline.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM routines WHERE id = ?", (routine_id,))
    conn.commit()
    
    deleted_count = cursor.rowcount
    conn.close()
    
    if deleted_count > 0:
        return {"deleted": routine_id, "message": "Routine deleted successfully"}
    else:
        return {"error": "Routine not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
