"""Database models for the application"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Session:
    """Session data model"""
    session_id: str
    session_name: str
    created_at: str
    updated_at: str
    message_count: Optional[int] = 0


@dataclass
class Message:
    """Message data model"""
    id: Optional[int]
    session_id: str
    role: str
    content: str
    timestamp: str


@dataclass
class User:
    """User data model"""
    user_id: int
    username: str
    email: str
    full_name: str
    age: int
    city: str
    country: str
    occupation: str
    department: str
    salary: float
    join_date: str
    is_active: bool
    last_login: Optional[str] = None