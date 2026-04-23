import sqlite3
import os
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "history.db")

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT,
            start_date TEXT,
            end_date TEXT,
            theme TEXT,
            summary_content TEXT,
            notion_url TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_report(task_type, start_date, end_date, theme, summary_content, notion_url=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO reports (task_type, start_date, end_date, theme, summary_content, notion_url, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task_type, start_date, end_date, theme, summary_content, notion_url, created_at))
    conn.commit()
    conn.close()

def get_all_reports():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
