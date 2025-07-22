"""Main chat application class"""

from ..ai import GeminiClient
from ..database.repositories.conversation_repo import ConversationRepository
from .services import SessionManager, MessageHandler


class ChatApplication:
    """Main chat application orchestrating all components"""
    
    def __init__(self):
        # Initialize components
        self.ai_client = GeminiClient()
        self.conversation_repo = ConversationRepository()
        
        # Initialize services
        self.session_manager = SessionManager(self.conversation_repo)
        self.message_handler = MessageHandler(self.ai_client, self.conversation_repo)
        
        # Create initial session
        self.current_session_id = self.session_manager.create_new_session()
    
    def send_message(self, message: str) -> str:
        """Send a message and get AI response"""
        return self.message_handler.send_message(self.current_session_id, message)
    
    def create_new_session(self) -> str:
        """Create a new chat session"""
        self.current_session_id = self.session_manager.create_new_session()
        return self.current_session_id
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to an existing session"""
        session_info = self.conversation_repo.get_session_info(session_id)
        if session_info:
            self.current_session_id = session_id
            return True
        return False
    
    def get_conversation_history(self, limit: int = 100):
        """Get current session's conversation history"""
        return self.conversation_repo.get_conversation_history(self.current_session_id, limit)
    
    def get_all_sessions(self):
        """Get all available sessions"""
        return self.conversation_repo.get_all_sessions()
    
    def clear_current_session(self):
        """Clear current session and create a new one"""
        self.conversation_repo.clear_session(self.current_session_id)
        self.current_session_id = self.session_manager.create_new_session()