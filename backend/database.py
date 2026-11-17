import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from .config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        tool_data TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    )
    """)
    
    # Study Plans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_plans (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        plan_data TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Student Progress / Analytics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_analytics (
        id TEXT PRIMARY KEY,
        concept TEXT NOT NULL,
        evidence TEXT,
        mastery_prob REAL,
        updated_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

# Auto-initialize database tables on module load
init_db()

# Session CRUD
def create_session(title: str = "New Chat") -> Dict[str, Any]:
    conn = get_db_connection()
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO chat_sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (session_id, title, now, now)
    )
    conn.commit()
    conn.close()
    return {"id": session_id, "title": title, "created_at": now, "updated_at": now}

def get_sessions() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM chat_sessions ORDER BY updated_at DESC").fetchall()
    sessions = [dict(row) for row in rows]
    conn.close()
    return sessions

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_session_title(session_id: str, title: str) -> bool:
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.execute(
        "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
        (title, now, session_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_session(session_id: str) -> bool:
    conn = get_db_connection()
    conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    cursor = conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# Message CRUD
def add_message(session_id: str, role: str, content: str, tool_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    conn = get_db_connection()
    msg_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    tool_data_json = json.dumps(tool_data) if tool_data else None
    
    # Ensure session exists
    session = conn.execute("SELECT id FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
    if not session:
        conn.execute(
            "INSERT INTO chat_sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (session_id, content[:30] + ("..." if len(content) > 30 else ""), now, now)
        )
    else:
        conn.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now, session_id))
        
    conn.execute(
        "INSERT INTO chat_messages (id, session_id, role, content, tool_data, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (msg_id, session_id, role, content, tool_data_json, now)
    )
    conn.commit()
    conn.close()
    return {
        "id": msg_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "tool_data": tool_data,
        "created_at": now
    }

def get_messages(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,)
    ).fetchall()
    messages = []
    for r in rows:
        d = dict(r)
        if d.get("tool_data"):
            try:
                d["tool_data"] = json.loads(d["tool_data"])
            except Exception:
                pass
        messages.append(d)
    conn.close()
    return messages

# Study Plan CRUD
def save_study_plan(title: str, plan_data: Dict[str, Any]) -> str:
    conn = get_db_connection()
    plan_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO study_plans (id, title, plan_data, created_at) VALUES (?, ?, ?, ?)",
        (plan_id, title, json.dumps(plan_data), now)
    )
    conn.commit()
    conn.close()
    return plan_id

def get_study_plans() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM study_plans ORDER BY created_at DESC").fetchall()
    plans = []
    for r in rows:
        d = dict(r)
        d["plan_data"] = json.loads(d["plan_data"])
        plans.append(d)
    conn.close()
    return plans
