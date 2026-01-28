import threading
import time
from datetime import datetime, timedelta
from database import get_all_routines
from database import update_routine
import platform

# Only import TTS on Windows (for PC monitoring)
# On cloud servers, reminders will be handled by push notifications
IS_WINDOWS = platform.system() == 'Windows'

if IS_WINDOWS:
    try:
        from tts import speak_background
        TTS_AVAILABLE = True
        print("✅ TTS available (Windows)")
    except ImportError:
        print("⚠️  TTS not available")
        TTS_AVAILABLE = False
        def speak_background(text, personality='default'):
            """Dummy function for when TTS is not available"""
            print(f"[TTS MOCK] Would speak: {text}")
else:
    TTS_AVAILABLE = False
    print("ℹ️  TTS disabled (cloud deployment - use push notifications)")
    def speak_background(text, personality='default'):
        """Dummy function for cloud deployment"""
        print(f"[TTS MOCK - Cloud] Would speak: {text}")
        # TODO: Send push notification to mobile app instead


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
        
        # Play TTS if available (Windows), otherwise just log
        if TTS_AVAILABLE:
            text = f"Yo! {routine.title} is coming up. Don't forget!"
            speak_background(text, routine.personality)
        else:
            # On cloud, this should trigger a push notification to the mobile app
            # For now, just log it
            print(f"[REMINDER] {routine.title} - Push notification should be sent here")
        
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
