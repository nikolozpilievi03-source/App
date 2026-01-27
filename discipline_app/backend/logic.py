import threading
import time
from datetime import datetime, timedelta
from database import get_all_routines
from tts import speak_background
from database import update_routine
def routine_datetime_local(routine):
    """Combines date and time into a local datetime object."""
    # This ignores timezones and just looks at the 'wall clock' time
    return datetime.combine(routine.routine_date, routine.routine_time)
def evaluate_routine_status(routine):
    """
    Evaluate and update routine status based on current time.
    Returns the updated routine object.
    """
    now = datetime.now()
    routine_time = datetime.combine(routine.routine_date, routine.routine_time)
    reminder_time = routine_time - timedelta(minutes=routine.reminder_minutes_before)
    miss_time = routine_time + timedelta(minutes=routine.grace_minutes_after)
    
    # Check if reminder should be triggered
    if (
        routine.status == "pending"
        and not routine.reminder_sent
        and now >= reminder_time
        and now < routine_time
    ):
        print(f"!!! TRIGGERING REMINDER FOR {routine.title} !!!")
        text = f"Yo! {routine.title} is coming up. Don't forget!"
        speak_background(text, routine.personality)
        
        routine.reminder_sent = True
        update_routine(routine)
    
    # Check if routine should be marked as missed
    elif routine.status == "pending" and now >= miss_time:
        print(f"--- MARKING {routine.title} AS MISSED ---")
        routine.status = "missed"
        routine.failures += 1
        routine.streak = 0
        
        update_routine(routine)
    
    # Always return the routine object
    return routine
def background_time_watcher():
    """This stays! It checks every second."""
    while True:
        try:
            routines = get_all_routines()
            for routine in routines:
                evaluate_routine_status(routine)
        except Exception as e:
            print(f"Watcher Error: {e}")

        time.sleep(1)
def start_background_thread():
    threading.Thread(
        target=background_time_watcher,
        daemon=True
    ).start()