import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SessionSummary:
    session_id: str
    session_name: str
    created_at: str
    message_count: int


class ConversationDB:
    """
    Database for storing AI conversation history and sessions.
    Acts as the AI's memory system, persisting conversations across sessions
    and allowing users to switch between different conversation contexts.
    """

    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                session_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_timestamp 
            ON conversations(session_id, timestamp)
        """)

        # Create index for sessions
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_created 
            ON sessions(created_at DESC)
        """)
        conn.commit()
        conn.close()

    def create_session(self, session_id: str, session_name: str | None = None):
        """Create a new session record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO sessions (session_id, session_name)
            VALUES (?, ?)
        """,
            (session_id, session_name),
        )

        conn.commit()
        conn.close()

    def update_session_name(self, session_id: str, session_name: str):
        """Update session name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE sessions 
            SET session_name = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE session_id = ?
        """,
            (session_name, session_id),
        )

        conn.commit()
        conn.close()

    def get_session_info(self, session_id: str) -> Dict | None:
        """Get session information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT session_id, session_name, created_at, updated_at
            FROM sessions 
            WHERE session_id = ?
        """,
            (session_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "session_id": row[0],
                "session_name": row[1],
                "created_at": row[2],
                "updated_at": row[3],
            }
        return None

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Ensure session exists
        cursor.execute(
            "INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,)
        )

        cursor.execute(
            """
            INSERT INTO conversations (session_id, role, content)
            VALUES (?, ?, ?)
        """,
            (session_id, role, content),
        )

        conn.commit()
        conn.close()

    def get_conversation_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[Dict]:
        """Get conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT role, content, timestamp 
            FROM conversations 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (session_id,))
        rows = cursor.fetchall()
        conn.close()

        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]} for row in rows
        ]

    def clear_session(self, session_id: str):
        """Clear all messages and session data for a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def get_all_sessions(self) -> List[Dict]:
        """Get all sessions with their names"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.session_id, s.session_name, s.created_at, 
               COUNT(c.id) as message_count
               FROM sessions s 
               LEFT JOIN conversations c ON s.session_id = c.session_id
               GROUP BY s.session_id, s.session_name, s.created_at
               ORDER BY s.created_at DESC"""
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "session_id": row[0],
                "session_name": row[1] or row[0],  # Fallback to session_id if no name
                "created_at": row[2],
                "message_count": row[3],
            }
            for row in rows
        ]
