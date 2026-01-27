"""
Quick Routine Creator - Creates routine X minutes from NOW
Usage: python create_routine_now.py
"""
import requests
from datetime import datetime, timedelta
import json
import sys

def create_routine_from_now(title, minutes_from_now=2):
    """Create a routine that happens X minutes from now"""
    
    now = datetime.now()
    routine_time = now + timedelta(minutes=minutes_from_now)
    
    # Reminder 1 minute before for quick testing
    reminder_minutes = 1 if minutes_from_now <= 5 else 5
    
    routine = {
        "title": title,
        "routine_date": routine_time.strftime("%Y-%m-%d"),
        "routine_time": routine_time.strftime("%H:%M"),  # HH:MM format only
        "personality": "hood",
        "reminder_minutes_before": reminder_minutes,
        "grace_minutes_after": 5
    }
    
    return routine, now, routine_time, reminder_minutes

# Example routines you can create
QUICK_ROUTINES = {
    "1": ("Workout", 2),
    "2": ("Reading", 5),
    "3": ("Meditation", 10),
    "4": ("Study Session", 15),
    "5": ("Water Break", 3),
}

print("=" * 60)
print("QUICK ROUTINE CREATOR")
print("=" * 60)
print("\nChoose a routine or create custom:")
print()
for key, (name, mins) in QUICK_ROUTINES.items():
    print(f"{key}. {name} (in {mins} minutes)")
print("6. Custom")
print()

choice = input("Enter choice (1-6): ").strip()

if choice in QUICK_ROUTINES:
    title, minutes = QUICK_ROUTINES[choice]
elif choice == "6":
    title = input("Routine name: ").strip()
    minutes = int(input("Minutes from now: ").strip())
else:
    print("Invalid choice! Using default: Workout in 2 minutes")
    title, minutes = "Workout", 2

# Create the routine
routine, now, routine_time, reminder_minutes = create_routine_from_now(title, minutes)

# Display info
print("\n" + "=" * 60)
print(f"Creating: {title}")
print("=" * 60)
print(f"Current time:    {now.strftime('%H:%M:%S')}")
print(f"Reminder at:     {(routine_time - timedelta(minutes=reminder_minutes)).strftime('%H:%M:%S')}")
print(f"Routine time:    {routine_time.strftime('%H:%M:%S')}")
print(f"Grace ends:      {(routine_time + timedelta(minutes=5)).strftime('%H:%M:%S')}")

# Send to API
try:
    print("\n📤 Sending to server...")
    response = requests.post(
        "http://127.0.0.1:8000/routines",
        json=[routine]
    )
    
    if response.status_code == 200:
        print("✅ Routine created!")
        
        # Show created routine
        created = response.json()
        print(f"\nCreated {created['created']} routine(s)")
        
        # Calculate wait time
        wait_time = (routine_time - timedelta(minutes=reminder_minutes) - now).total_seconds()
        wait_mins = int(wait_time // 60)
        wait_secs = int(wait_time % 60)
        
        print(f"\n🔊 Reminder in: {wait_mins}m {wait_secs}s")
        print(f'   Message: "Yo! {title} is coming up. Don\'t forget!"')
        
        print("\n" + "=" * 60)
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ Server not running!")
    print("Start it with: python main.py")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Show JSON format
print("\nJSON sent to server:")
print(json.dumps(routine, indent=2))
