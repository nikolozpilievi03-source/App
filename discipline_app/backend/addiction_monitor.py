"""
Addiction Monitoring System for Discipline App
Monitors browser activity and triggers AI warnings OR custom MP3 for harmful sites

FEATURES:
- Real-time browser monitoring (Chrome, Firefox, Edge, Brave)
- URL pattern detection (porn, gambling, time-wasting sites)
- AI voice warnings OR custom MP3 files
- Logging to database
- Cooldown to prevent spam
- Configurable block lists per category
"""

import time
import sqlite3
from datetime import datetime
import psutil
import win32gui
import win32process
from urllib.parse import urlparse
import tts
import pygame
import os

# Initialize pygame for custom audio
pygame.mixer.init()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Custom audio files (put your MP3 files in a 'custom_audio' folder)
CUSTOM_AUDIO_DIR = "custom_audio"

CUSTOM_AUDIO_FILES = {
    'porn': 'porn_warning.mp3',      # Your custom MP3 for porn warnings
    'gambling': 'gambling_warning.mp3',  # Your custom MP3 for gambling
    'social_media': 'social_media_warning.mp3',
    'gaming': 'gaming_warning.mp3',
}

# Set to True to use custom MP3, False to use AI voice
USE_CUSTOM_AUDIO = {
    'porn': True,        # Will play custom_audio/porn_warning.mp3
    'gambling': True,    # Will play custom_audio/gambling_warning.mp3
    'social_media': False,  # Will use AI voice
    'gaming': False,     # Will use AI voice
}

# Blocked URL patterns
PORN_PATTERNS = [
    'pornhub', 'xvideos', 'xnxx', 'redtube', 'youporn',
    'xhamster', 'tube8', 'spankwire', 'keezmovies',
    'porn', 'xxx', 'sex', 'adult', 'nsfw',
    'onlyfans', 'chaturbate', 'stripchat', 'cam4',
    'livejasmin', 'bongacams', 'myfreecams'
]

GAMBLING_PATTERNS = [
    'casino', 'poker', 'betting', 'bet365', 'pokerstars',
    'gamble', 'slots', 'blackjack', 'roulette',
    'sportbet', 'bwin', '888casino', 'draftkings',
    'fanduel', 'bovada', 'stake.com'
]

# AI voice warning messages (used when custom audio is disabled)
AI_WARNINGS = {
    'porn': [
        "Yo! Stop right there. You're better than this. Close that tab NOW!",
        "Hey! What are you doing? Remember your goals. Close this immediately!",
        "This isn't who you want to be. Close it and get back on track!",
    ],
    'gambling': [
        "Hold up! Gambling will drain your wallet. Close this now!",
        "Yo! Don't throw your money away. Close that tab!",
        "Stop! You're about to make a mistake. Close it!",
    ],
}

# Cooldown (seconds between warnings for same category)
WARNING_COOLDOWN = 30

# Which categories to monitor
MONITOR_PORN = True        # Set to True to monitor porn sites
MONITOR_GAMBLING = True    # Set to True to monitor gambling

# Use custom MP3 or AI voice
use_custom_audio = {
    'porn': True,          # True = use MP3, False = use AI voice
    'gambling': True,
}

# ============================================================================
# AUDIO PLAYBACK
# ============================================================================

def play_custom_audio(audio_file):
    """Play a custom MP3 file"""
    try:
        file_path = os.path.join(CUSTOM_AUDIO_DIR, audio_file)
        
        if not os.path.exists(file_path):
            print(f"⚠️  Custom audio not found: {file_path}")
            print(f"   Create folder: {CUSTOM_AUDIO_DIR}/")
            print(f"   Add file: {audio_file}")
            return False
        
        print(f"🔊 Playing custom audio: {audio_file}")
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        print(f"✅ Custom audio finished")
        return True
        
    except Exception as e:
        print(f"❌ Error playing custom audio: {e}")
        return False

def play_warning(category, personality='strict'):
    """Play warning - either custom MP3 or AI voice"""
    
    # Check if custom audio should be used
    use_custom = USE_CUSTOM_AUDIO.get(category, False)
    
    if use_custom:
        # Try to play custom audio
        audio_file = CUSTOM_AUDIO_FILES.get(category)
        if audio_file:
            success = play_custom_audio(audio_file)
            if success:
                return
            else:
                print(f"⚠️  Falling back to AI voice")
    
    # Use AI voice (either by choice or as fallback)
    warnings = AI_WARNINGS.get(category, ["Stop! Close this now!"])
    message = warnings[0]  # Use first warning (can randomize later)
    
    print(f"🔊 Playing AI voice warning")
    tts.speak_background(message, personality)

# ============================================================================
# DATABASE
# ============================================================================

def init_addiction_db():
    """Initialize database tables"""
    conn = sqlite3.connect('discipline.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS block_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            blocks_count INTEGER DEFAULT 0,
            UNIQUE(date, category)
        )
    """)
    
    conn.commit()
    conn.close()

def log_block_attempt(category, url, title, audio_type):
    """Log blocked attempt to database"""
    try:
        conn = sqlite3.connect('discipline.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO block_logs (category, url, title, timestamp, audio_type)
            VALUES (?, ?, ?, ?, ?)
        """, (category, url, title, datetime.now().isoformat(), audio_type))
        
        # Update daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            INSERT INTO block_stats (date, category, blocks_count)
            VALUES (?, ?, 1)
            ON CONFLICT(date, category)
            DO UPDATE SET blocks_count = blocks_count + 1
        """, (today, category))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging: {e}")

def get_block_stats(days=7):
    """Get blocking statistics for last N days"""
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

# ============================================================================
# BROWSER MONITORING
# ============================================================================

def get_active_window_info():
    """Get info about currently active window"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        try:
            process = psutil.Process(pid)
            process_name = process.name().lower()
        except:
            process_name = ""
        
        return {
            'title': title,
            'process': process_name,
            'pid': pid
        }
    except:
        return None

def is_browser(process_name):
    """Check if process is a browser"""
    browsers = ['chrome', 'firefox', 'edge', 'brave', 'opera', 'msedge']
    return any(browser in process_name for browser in browsers)

def check_url_category(text):
    """Check if URL/title contains blocked patterns"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Check porn patterns
    if MONITOR_PORN:
        for pattern in PORN_PATTERNS:
            if pattern in text_lower:
                return 'porn'
    
    # Check gambling patterns
    if MONITOR_GAMBLING:
        for pattern in GAMBLING_PATTERNS:
            if pattern in text_lower:
                return 'gambling'
    
    return None

# ============================================================================
# MAIN MONITORING LOOP
# ============================================================================

def addiction_monitor_loop():
    """Main monitoring loop - runs forever"""
    
    print("\n" + "="*60)
    print("🛡️  ADDICTION MONITOR STARTED")
    print("="*60)
    print(f"Monitoring: {', '.join([k for k,v in {'Porn': MONITOR_PORN, 'Gambling': MONITOR_GAMBLING}.items() if v])}")
    print(f"Custom audio folder: {CUSTOM_AUDIO_DIR}/")
    print(f"Cooldown: {WARNING_COOLDOWN} seconds")
    print("="*60 + "\n")
    
    last_warning_time = {}
    
    while True:
        try:
            # Get active window
            window_info = get_active_window_info()
            
            if not window_info:
                time.sleep(2)
                continue
            
            # Only monitor browsers
            if not is_browser(window_info['process']):
                time.sleep(2)
                continue
            
            # Check if URL contains harmful patterns
            category = check_url_category(window_info['title'])
            
            if category:
                # Check cooldown
                now = time.time()
                last_time = last_warning_time.get(category, 0)
                
                if now - last_time > WARNING_COOLDOWN:
                    print(f"\n{'='*60}")
                    print(f"⚠️  BLOCKED: {category.upper()}")
                    print(f"Title: {window_info['title'][:80]}")
                    print(f"{'='*60}")
                    
                    # Determine audio type
                    audio_type = 'custom_mp3' if USE_CUSTOM_AUDIO.get(category) else 'ai_voice'
                    
                    # Play warning
                    play_warning(category)
                    
                    # Log it
                    log_block_attempt(
                        category,
                        window_info['title'],
                        window_info['title'],
                        audio_type
                    )
                    
                    # Update cooldown
                    last_warning_time[category] = now
                    
                    print(f"✅ Warning played ({audio_type})")
                    print(f"Next warning in {WARNING_COOLDOWN}s")
                    print("="*60 + "\n")
            
            # Check every 2 seconds
            time.sleep(2)
            
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(5)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_custom_audio_folder():
    """Create custom audio folder and show instructions"""
    if not os.path.exists(CUSTOM_AUDIO_DIR):
        os.makedirs(CUSTOM_AUDIO_DIR)
        print(f"📁 Created folder: {CUSTOM_AUDIO_DIR}/")
    
    print("\n" + "="*60)
    print("📁 CUSTOM AUDIO SETUP")
    print("="*60)
    print(f"\nTo use custom MP3 warnings:")
    print(f"1. Put your MP3 files in: {CUSTOM_AUDIO_DIR}/")
    print(f"2. Name them:")
    for category, filename in CUSTOM_AUDIO_FILES.items():
        status = "✅ ACTIVE" if USE_CUSTOM_AUDIO.get(category) else "⏸️  AI Voice"
        print(f"   - {filename} ({status})")
    print(f"\n3. Edit USE_CUSTOM_AUDIO in code to enable/disable")
    print("="*60 + "\n")

def show_stats():
    """Display blocking statistics"""
    stats = get_block_stats(7)
    
    if not stats:
        print("No blocks recorded yet")
        return
    
    print("\n" + "="*60)
    print("📊 BLOCKING STATISTICS (Last 7 Days)")
    print("="*60)
    
    by_category = {}
    for date, category, count in stats:
        if category not in by_category:
            by_category[category] = 0
        by_category[category] += count
    
    for category, total in by_category.items():
        print(f"{category.upper()}: {total} blocks")
    
    print("="*60 + "\n")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Initialize
    init_addiction_db()
    setup_custom_audio_folder()
    
    # Show current stats
    show_stats()
    
    # Ask user if ready
    print("Ready to start monitoring?")
    print("Press ENTER to start, or CTRL+C to cancel")
    input()
    
    # Start monitoring
    try:
        addiction_monitor_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped")
        show_stats()
