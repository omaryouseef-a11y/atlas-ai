import sqlite3
import os

DB_PATH = 'atlas.db'

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Projects/Episodes Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS episodes (
        id TEXT PRIMARY KEY,
        title TEXT,
        status TEXT, -- pending, in_progress, QA_failed, ready_for_approval, published
        current_phase TEXT, -- script, voice, video, editing
        budget_limit REAL,
        total_cost REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Jobs/Tasks Table (The recovery system)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        episode_id TEXT,
        department TEXT, -- e.g., ScriptEngine, MotionEngine
        task_type TEXT, -- e.g., generate_prompt, generate_video, generate_voice
        input_data TEXT,
        output_data TEXT,
        status TEXT, -- pending, running, completed, failed
        cost REAL DEFAULT 0.0,
        error_log TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (episode_id) REFERENCES episodes (id)
    )
    ''')

    # 3. Assets Library Table (For reusability)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        asset_type TEXT, -- character_image, voice_model, background, music
        name TEXT,
        file_path TEXT,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print('🏗️ Atlas Core Database initialized successfully.')

if __name__ == '__main__':
    setup_database()
