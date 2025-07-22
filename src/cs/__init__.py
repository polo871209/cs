"""CS - AI Chat Application with Memory

A modern AI chat application with persistent conversation history,
session management, and external tool integration.
"""

from .chat import ChatApplication
from .cli import ChatCLI
from .config import settings

__version__ = "0.1.0"
__all__ = ["ChatApplication", "ChatCLI", "settings"]