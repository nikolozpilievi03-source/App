"""
Discipline App Backend API
Handles routine reminders, logging, and statistics
This version is deployable to cloud (no Windows-specific code)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import os
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)  # Allow Flutter app to connect

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE = 'discipline.db'

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

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize all database tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Block logs table
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
    
    # Block stats table
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
    
    # Routines table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            time TEXT NOT NULL,
            days TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)
    
    # Routine completions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routine_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            routine_id INTEGER NOT NULL,
            completed_at TEXT NOT NULL,
            FOREIGN KEY (routine_id) REFERENCES routines (id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# ============================================================================
# API ENDPOINTS - BLOCKING & WARNINGS
# ============================================================================

@app.route('/api/check-url', methods=['POST'])
def check_url():
    """Check if a URL should trigger a warning"""
    data = request.json
    url = data.get('url', '').lower()
    
    # Check against patterns
    category = None
    for pattern in PORN_PATTERNS:
        if pattern in url:
            category = 'porn'
            break
    
    if not category:
        for pattern in GAMBLING_PATTERNS:
            if pattern in url:
                category = 'gambling'
                break
    
    if category:
        return jsonify({
            'blocked': True,
            'category': category,
            'message': f'Warning: {category} content detected'
        })
    
    return jsonify({'blocked': False})

@app.route('/api/log-block', methods=['POST'])
def log_block():
    """Log a blocked attempt from the mobile app"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default')
        category = data.get('category')
        url = data.get('url', '')
        title = data.get('title', '')
        audio_type = data.get('audio_type', 'warning')
        
        conn = get_db()
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
        
        return jsonify({'success': True, 'message': 'Block logged'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get blocking statistics"""
    user_id = request.args.get('user_id', 'default')
    days = int(request.args.get('days', 7))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, category, blocks_count
        FROM block_stats
        WHERE user_id = ? AND date >= date('now', '-' || ? || ' days')
        ORDER BY date DESC
    """, (user_id, days))
    
    rows = cursor.fetchall()
    conn.close()
    
    stats = []
    total_by_category = {}
    
    for row in rows:
        stats.append({
            'date': row['date'],
            'category': row['category'],
            'count': row['blocks_count']
        })
        
        category = row['category']
        if category not in total_by_category:
            total_by_category[category] = 0
        total_by_category[category] += row['blocks_count']
    
    return jsonify({
        'daily_stats': stats,
        'totals': total_by_category
    })

# ============================================================================
# API ENDPOINTS - ROUTINES
# ============================================================================

@app.route('/api/routines', methods=['GET'])
def get_routines():
    """Get all routines for a user"""
    user_id = request.args.get('user_id', 'default')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM routines
        WHERE user_id = ? AND active = 1
        ORDER BY time
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    routines = []
    for row in rows:
        routines.append({
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'time': row['time'],
            'days': row['days'],
            'created_at': row['created_at']
        })
    
    return jsonify(routines)

@app.route('/api/routines', methods=['POST'])
def create_routine():
    """Create a new routine"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default')
        title = data['title']
        description = data.get('description', '')
        time = data['time']  # Format: "14:30"
        days = data['days']  # Format: "Mon,Wed,Fri" or "Daily"
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO routines (user_id, title, description, time, days, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, title, description, time, days, datetime.now().isoformat()))
        
        routine_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'routine_id': routine_id,
            'message': 'Routine created'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/routines/<int:routine_id>', methods=['DELETE'])
def delete_routine(routine_id):
    """Delete a routine"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE routines SET active = 0 WHERE id = ?", (routine_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Routine deleted'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/routines/<int:routine_id>/complete', methods=['POST'])
def complete_routine(routine_id):
    """Mark a routine as completed"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO routine_completions (routine_id, completed_at)
            VALUES (?, ?)
        """, (routine_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Routine marked complete'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/routines/completions', methods=['GET'])
def get_completions():
    """Get routine completion history"""
    user_id = request.args.get('user_id', 'default')
    days = int(request.args.get('days', 7))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.title, rc.completed_at
        FROM routine_completions rc
        JOIN routines r ON rc.routine_id = r.id
        WHERE r.user_id = ? AND rc.completed_at >= datetime('now', '-' || ? || ' days')
        ORDER BY rc.completed_at DESC
    """, (user_id, days))
    
    rows = cursor.fetchall()
    conn.close()
    
    completions = []
    for row in rows:
        completions.append({
            'title': row['title'],
            'completed_at': row['completed_at']
        })
    
    return jsonify(completions)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'app': 'Discipline App Backend',
        'version': '1.0',
        'status': 'running'
    })

# ============================================================================
# SCHEDULED TASKS (Optional - for future reminder notifications)
# ============================================================================

def check_reminders():
    """Check if any routines need reminders (runs every minute)"""
    # This would send push notifications to mobile devices
    # You can implement this later with Firebase Cloud Messaging
    pass

# Initialize scheduler for reminders
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_reminders, trigger="interval", minutes=1)
scheduler.start()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 DISCIPLINE APP BACKEND STARTING")
    print("="*60)
    
    # Initialize database
    init_db()
    
    print("\n📋 Available API Endpoints:")
    print("  GET  /health                        - Health check")
    print("  POST /api/check-url                 - Check if URL is blocked")
    print("  POST /api/log-block                 - Log a blocked attempt")
    print("  GET  /api/stats                     - Get blocking statistics")
    print("  GET  /api/routines                  - Get all routines")
    print("  POST /api/routines                  - Create new routine")
    print("  DELETE /api/routines/<id>           - Delete routine")
    print("  POST /api/routines/<id>/complete    - Mark routine complete")
    print("  GET  /api/routines/completions      - Get completion history")
    print("\n" + "="*60)
    print("🌐 Server will start on http://0.0.0.0:5000")
    print("="*60 + "\n")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)