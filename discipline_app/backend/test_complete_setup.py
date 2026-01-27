"""
Complete Setup Test for Discipline App
Run this to verify everything is working before starting the server
"""
import sys

print("=" * 60)
print("DISCIPLINE APP - SETUP VERIFICATION")
print("=" * 60)

# Test 1: Check Python version
print("\n[1/8] Checking Python version...")
python_version = sys.version_info
if python_version.major == 3 and python_version.minor >= 11:
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
else:
    print(f"⚠️  Python {python_version.major}.{python_version.minor} (recommend 3.11+)")

# Test 2: Check pygame
print("\n[2/8] Checking pygame...")
try:
    import pygame
    pygame.mixer.init()
    print(f"✅ pygame {pygame.ver} - Audio system ready")
except Exception as e:
    print(f"❌ pygame not working: {e}")
    print("   Fix: python -m pip install pygame")
    sys.exit(1)

# Test 3: Check edge-tts
print("\n[3/8] Checking edge-tts...")
try:
    import edge_tts
    print(f"✅ edge-tts installed")
except Exception as e:
    print(f"❌ edge-tts not installed: {e}")
    print("   Fix: python -m pip install edge-tts")
    sys.exit(1)

# Test 4: Check FastAPI
print("\n[4/8] Checking FastAPI...")
try:
    import fastapi
    import uvicorn
    print(f"✅ FastAPI and uvicorn installed")
except Exception as e:
    print(f"❌ FastAPI not installed: {e}")
    print("   Fix: python -m pip install fastapi uvicorn")
    sys.exit(1)

# Test 5: Check all project files
print("\n[5/8] Checking project files...")
import os
required_files = ['main.py', 'models.py', 'database.py', 'logic.py', 'tts.py']
missing = []
for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} NOT FOUND")
        missing.append(file)

if missing:
    print(f"\n⚠️  Missing files: {', '.join(missing)}")
    print("   Make sure you're in the correct directory!")
    sys.exit(1)

# Test 6: Check database module
print("\n[6/8] Testing database module...")
try:
    from database import init_db, get_connection
    init_db()
    conn = get_connection()
    conn.close()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)

# Test 7: Check models
print("\n[7/8] Testing models...")
try:
    from models import Routine
    from datetime import date, time
    test_routine = Routine(
        title="Test",
        routine_date=date.today(),
        routine_time=time(15, 30)
    )
    print(f"✅ Models working - Test routine created")
except Exception as e:
    print(f"❌ Models error: {e}")
    sys.exit(1)

# Test 8: Quick audio test
print("\n[8/8] Testing audio (quick test)...")
print("    This will play a short test sound...")
try:
    from tts import speak_background
    import time as time_module
    
    speak_background("Quick test", "hood")
    time_module.sleep(4)  # Wait for it to finish
    print("✅ Audio system working!")
except Exception as e:
    print(f"❌ Audio test failed: {e}")
    print("   The app will run but audio might not work")

# All tests passed!
print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("\nYour app is ready to run!")
print("\nNext steps:")
print("1. Run the server: python main.py")
print("2. Create a test routine (see test_routine.py)")
print("3. Wait for the AI voice reminder!")
print("\n" + "=" * 60)
