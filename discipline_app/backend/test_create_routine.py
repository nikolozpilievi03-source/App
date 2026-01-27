"""
Test Routine Creator
Creates a routine that will trigger in 2 minutes so you can test the audio reminder
"""
import requests
from datetime import datetime, timedelta

print("=" * 60)
print("CREATING TEST ROUTINE")
print("=" * 60)

# Calculate times
now = datetime.now()
routine_time = now + timedelta(minutes=2)
reminder_time = routine_time - timedelta(minutes=1)

print(f"\nCurrent time: {now.strftime('%H:%M:%S')}")
print(f"Routine scheduled for: {routine_time.strftime('%H:%M:%S')}")
print(f"Reminder will play at: {reminder_time.strftime('%H:%M:%S')}")
print(f"Grace period ends at: {(routine_time + timedelta(minutes=3)).strftime('%H:%M:%S')}")

# Create the routine
routine = {
    "title": "Test Workout",
    "routine_date": routine_time.strftime("%Y-%m-%d"),
    "routine_time": routine_time.strftime("%H:%M"),
    "personality": "hood",
    "reminder_minutes_before": 1,  # Remind 1 minute before
    "grace_minutes_after": 3       # 3 minute grace period
}

try:
    print("\n📤 Sending to API...")
    response = requests.post(
        "http://127.0.0.1:8000/routines",
        json=[routine]
    )
    
    if response.status_code == 200:
        print("✅ Routine created successfully!")
        print(f"\nResponse: {response.json()}")
        
        print("\n" + "=" * 60)
        print("⏰ WAIT FOR THE REMINDER!")
        print("=" * 60)
        print(f"\n🔊 In about 1 minute, you should hear:")
        print(f'   "Yo! Test Workout is coming up. Don\'t forget!"')
        print(f"\nIf you don't complete it within 3 minutes after {routine_time.strftime('%H:%M')},")
        print(f"it will be marked as MISSED (red X)")
        print("\n" + "=" * 60)
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to server!")
    print("\nMake sure the backend is running:")
    print("1. Open another terminal/PyCharm tab")
    print("2. Run: python main.py")
    print("3. Wait for 'Uvicorn running on http://127.0.0.1:8000'")
    print("4. Then run this script again")
except Exception as e:
    print(f"\n❌ Error: {e}")
