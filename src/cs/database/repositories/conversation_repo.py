"""Conversation repository for database operations"""

from typing import Dict, List, Optional

from ..base import BaseRepository
from ..models import Session 


class ConversationRepository(BaseRepository):
    """
    Repository for storing AI conversation history and sessions.
    Acts as the AI's memory system, persisting conversations across sessions
    and allowing users to switch between different conversation contexts.
    """

    def __init__(self):
        super().__init__()
        self.init_database()

    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Create sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
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

                # Create indexes for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session_timestamp 
                    ON conversations(session_id, timestamp)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sessions_created 
                    ON sessions(created_at DESC)
                """)
                conn.commit()
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            raise

    def create_session(self, session_id: str, session_name: Optional[str] = None) -> None:
        """Create a new session record"""
        if not session_id or not session_id.strip():
            raise ValueError("Session ID cannot be empty")
        
        self.execute_query(
            "INSERT OR IGNORE INTO sessions (session_id, session_name) VALUES (?, ?)",
            (session_id, session_name)
        )

    def update_session_name(self, session_id: str, session_name: str) -> None:
        """Update session name"""
        if not session_id or not session_name:
            raise ValueError("Session ID and name cannot be empty")
        
        self.execute_query(
            """UPDATE sessions 
               SET session_name = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE session_id = ?""",
            (session_name, session_id)
        )

    def get_session_info(self, session_id: str) -> Optional[Session]:
        """Get session information"""
        if not session_id:
            return None
            
        row = self.execute_query(
            """SELECT session_id, session_name, created_at, updated_at
               FROM sessions WHERE session_id = ?""",
            (session_id,),
            fetch_one=True
        )

        if row:
            return Session(
                session_id=row[0],
                session_name=row[1] or row[0],
                created_at=row[2],
                updated_at=row[3],
            )
        return None

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        if not session_id or not role or content is None:
            raise ValueError("Session ID, role, and content are required")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Ensure session exists
                cursor.execute(
                    "INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,)
                )
                cursor.execute(
                    """INSERT INTO conversations (session_id, role, content)
                       VALUES (?, ?, ?)""",
                    (session_id, role, content),
                )
                conn.commit()
        except Exception as e:
            print(f"❌ Error adding message: {e}")
            raise

    def get_conversation_history(
        self, session_id: str, limit: Optional[int] = 100
    ) -> List[Dict]:
        """Get conversation history for a session with default limit for memory efficiency"""
        if not session_id:
            return []
            
        query = """
            SELECT role, content, timestamp 
            FROM conversations 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """
        
        params = (session_id,)
        if limit:
            query += " LIMIT ?"
            params = (session_id, limit)
            
        rows = self.execute_query(query, params, fetch_all=True)
        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]} 
            for row in (rows or [])
        ]

    def clear_session(self, session_id: str) -> None:
        """Clear all messages and session data for a specific session"""
        if not session_id:
            raise ValueError("Session ID cannot be empty")
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
        except Exception as e:
            print(f"❌ Error clearing session: {e}")
            raise

    def get_all_sessions(self) -> List[Session]:
        """Get all sessions with their names"""
        rows = self.execute_query(
            """SELECT s.session_id, s.session_name, s.created_at, s.updated_at,
                      COUNT(c.id) as message_count
               FROM sessions s 
               LEFT JOIN conversations c ON s.session_id = c.session_id
               GROUP BY s.session_id, s.session_name, s.created_at
               ORDER BY s.created_at DESC""",
            fetch_all=True
        )

        return [
            Session(
                session_id=row[0],
                session_name=row[1] or row[0],
                created_at=row[2],
                updated_at=row[3],
                message_count=row[4],
            )
            for row in (rows or [])
        ]
