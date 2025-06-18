import sqlite3
from typing import Dict, List, Optional


class ConversationDB:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_timestamp 
            ON conversations(session_id, timestamp)
        """)

        conn.commit()
        conn.close()

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

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
        """Clear all messages for a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def get_all_sessions(self) -> List[str]:
        """Get all unique session IDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT session_id FROM conversations ORDER BY created_at DESC"
        )
        sessions = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sessions
