from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel as PydanticBaseModel
from models import Routine
from logic import evaluate_routine_status, background_time_watcher
from database import (
    init_db,
    insert_routine,
    get_all_routines,
    update_routine,
    update_routine_details,
    delete_routine_by_id,
    log_block,
    get_block_stats_rows,
)
import threading
import platform
import os

app = FastAPI(title="Discipline App")

# Add CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if running on Windows (for local development with addiction monitor)
IS_WINDOWS = platform.system() == 'Windows'

if IS_WINDOWS:
    try:
        from addiction_monitor import addiction_monitor_loop, init_addiction_db
        ADDICTION_MONITOR_AVAILABLE = True
    except ImportError:
        print("⚠️  Addiction monitor not available (Windows-only feature)")
        ADDICTION_MONITOR_AVAILABLE = False

        def init_addiction_db():
            pass
else:
    ADDICTION_MONITOR_AVAILABLE = False

    def init_addiction_db():
        # Block tables are created by database.init_db() (works for
        # both Postgres and SQLite), so nothing extra needed here.
        pass


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


@app.get("/")
def root():
    return {
        "status": "Backend running successfully",
        "platform": platform.system(),
        "database": "postgres" if os.environ.get("DATABASE_URL") else "sqlite",
        "addiction_monitor": "active" if ADDICTION_MONITOR_AVAILABLE else "mobile-only"
    }


@app.post("/routines")
def create_routines(routines: List[Routine]):
    for routine in routines:
        insert_routine(routine)
    return {"created": len(routines)}


@app.get("/routines")
def list_routines(user_id: str = "default"):
    # Filter directly in SQL (much faster than fetching everything)
    user_routines = get_all_routines(user_id)

    updated = []
    for routine in user_routines:
        updated_routine = evaluate_routine_status(routine)
        update_routine(updated_routine)
        updated.append(updated_routine)
    return updated


class RoutineUpdate(PydanticBaseModel):
    title: Optional[str] = None
    routine_date: Optional[str] = None
    routine_time: Optional[str] = None
    personality: Optional[str] = None


@app.put("/routines/{routine_id}")
def edit_routine(routine_id: int, updates: RoutineUpdate):
    """Update a routine's editable fields (title, date, time, personality)"""
    changed = update_routine_details(
        routine_id,
        title=updates.title,
        routine_date=updates.routine_date,
        routine_time=updates.routine_time,
        personality=updates.personality,
    )
    if changed:
        return {"updated": routine_id, "message": "Routine updated successfully"}
    return {"error": "Routine not found or nothing to update"}


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


@app.delete("/routines/{routine_id}")
def delete_routine(routine_id: int):
    """Delete a routine by ID"""
    if delete_routine_by_id(routine_id):
        return {"deleted": routine_id, "message": "Routine deleted successfully"}
    return {"error": "Routine not found"}


@app.get("/addiction-stats")
def get_addiction_stats(user_id: str = None):
    """Get addiction blocking statistics"""
    stats = get_block_stats_rows(7, user_id)

    # Format for API response
    by_category = {}
    by_date = {}

    for date_str, category, count in stats:
        if category not in by_category:
            by_category[category] = 0
        by_category[category] += count

        if date_str not in by_date:
            by_date[date_str] = {}
        by_date[date_str][category] = count

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
        log_block(user_id, category, url, title, audio_type)
        return {"success": True, "message": "Block logged"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)