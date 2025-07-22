"""Base repository with common database functionality"""

import sqlite3
from contextlib import contextmanager
from abc import ABC

from ..config import settings


class BaseRepository(ABC):
    """Base repository class with common database operations"""
    
    def __init__(self):
        self.db_path = settings.database_path

    @contextmanager
    def get_connection(self):
        """Context manager for database connections with error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = False):
        """Execute a query with error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            raise
