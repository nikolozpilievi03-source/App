"""
Smart Routine Creator
Automatically creates routines in the future with correct time format
"""
import requests
from datetime import datetime, timedelta
import json

print("=" * 60)
print("SMART ROUTINE CREATOR")
print("=" * 60)

# Get current time
now = datetime.now()
print(f"\nCurrent time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# Ask user for routine details
print("\n" + "=" * 60)
print("CREATE YOUR ROUTINE")
print("=" * 60)

title = input("\nRoutine title (e.g., Workout, Study, Meditate): ").strip()
if not title:
    title = "My Routine"

print("\nWhen should this routine happen?")
print("1. In 2 minutes (for quick testing)")
print("2. In 10 minutes")
print("3. In 1 hour")
print("4. Custom time (HH:MM format)")

choice = input("\nChoose option (1-4): ").strip()

if choice == "1":
    routine_time = now + timedelta(minutes=2)
    reminder_minutes = 1
elif choice == "2":
    routine_time = now + timedelta(minutes=10)
    reminder_minutes = 5
elif choice == "3":
    routine_time = now + timedelta(hours=1)
    reminder_minutes = 10
elif choice == "4":
    time_input = input("Enter time (HH:MM, e.g., 14:30): ").strip()
    try:
        hour, minute = map(int, time_input.split(':'))
        routine_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If time is in the past, set it for tomorrow
        if routine_time < now:
            routine_time += timedelta(days=1)
        
        # Calculate reminder time (10 minutes before)
        reminder_minutes = 10
    except:
        print("Invalid time format! Using default: 2 minutes from now")
        routine_time = now + timedelta(minutes=2)
        reminder_minutes = 1
else:
    # Default: 2 minutes from now
    routine_time = now + timedelta(minutes=2)
    reminder_minutes = 1

# Calculate times
reminder_time = routine_time - timedelta(minutes=reminder_minutes)
grace_end = routine_time + timedelta(minutes=5)

# Create routine with CORRECT format (no timezone, no seconds)
routine = {
    "title": title,
    "routine_date": routine_time.strftime("%Y-%m-%d"),  # YYYY-MM-DD
    "routine_time": routine_time.strftime("%H:%M"),     # HH:MM only
    "personality": "hood",
    "reminder_minutes_before": reminder_minutes,
    "grace_minutes_after": 5
}

print("\n" + "=" * 60)
print("ROUTINE DETAILS")
print("=" * 60)
print(f"Title: {routine['title']}")
print(f"Date: {routine['routine_date']}")
print(f"Time: {routine['routine_time']}")
print(f"Personality: {routine['personality']}")
print(f"\n⏰ Timeline:")
print(f"  Current time:     {now.strftime('%H:%M:%S')}")
print(f"  Reminder plays:   {reminder_time.strftime('%H:%M:%S')} ({reminder_minutes} min before)")
print(f"  Routine time:     {routine_time.strftime('%H:%M:%S')}")
print(f"  Grace ends:       {grace_end.strftime('%H:%M:%S')} (marked missed if not done)")

# Send to API
try:
    print("\n📤 Sending to API...")
    response = requests.post(
        "http://127.0.0.1:8000/routines",
        json=[routine]
    )
    
    if response.status_code == 200:
        print("✅ Routine created successfully!")
        print(f"\nAPI Response: {json.dumps(response.json(), indent=2)}")
        
        # Calculate wait time
        wait_seconds = (reminder_time - now).total_seconds()
        wait_minutes = int(wait_seconds // 60)
        wait_seconds_rem = int(wait_seconds % 60)
        
        print("\n" + "=" * 60)
        print("⏰ WAIT FOR THE REMINDER!")
        print("=" * 60)
        print(f"\n🔊 In {wait_minutes} min {wait_seconds_rem} sec, you'll hear:")
        print(f'   "Yo! {title} is coming up. Don\'t forget!"')
        print(f"\nKeep the backend (main.py) running and wait!")
        print("=" * 60)
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to server!")
    print("\nMake sure the backend is running:")
    print("Run in another terminal: python main.py")
except Exception as e:
    print(f"\n❌ Error: {e}")

# Show the created routine JSON
print("\n" + "=" * 60)
print("ROUTINE JSON (for reference)")
print("=" * 60)
print(json.dumps(routine, indent=2))
