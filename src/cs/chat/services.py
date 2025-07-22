"""Chat service for handling AI conversations"""

import uuid
from datetime import datetime
from typing import List

from google.genai import types

from ..ai import GeminiClient
from ..database.repositories.conversation_repo import ConversationRepository
from ..tools import fetch_current_weather


class SessionManager:
    """Manages chat sessions"""
    
    def __init__(self, conversation_repo: ConversationRepository):
        self.conversation_repo = conversation_repo
    
    def create_new_session(self) -> str:
        """Create a new unique session ID"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        self.conversation_repo.create_session(session_id)
        print(f"🆕 New session created: {session_id}")
        return session_id


class MessageHandler:
    """Handles message processing and AI interactions"""
    
    def __init__(self, ai_client: GeminiClient, conversation_repo: ConversationRepository):
        self.ai_client = ai_client
        self.conversation_repo = conversation_repo
    
    def build_conversation_contents(self, session_id: str, user_input: str) -> List[types.Content]:
        """Build conversation contents using genai types structure"""
        history = self.conversation_repo.get_conversation_history(session_id)
        contents = []

        # Add conversation history
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])],
                )
            )

        # Add current user input
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)],
            )
        )

        return contents
    
    def send_message(self, session_id: str, user_input: str) -> str:
        """Send message to AI and store in database"""
        contents = self.build_conversation_contents(session_id, user_input)
        
        # Configure response format
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            tools=[fetch_current_weather],  # TODO: Add user search tool
        )

        try:
            # Get AI response with streaming
            stream = self.ai_client.generate_content_stream(
                contents=contents,
                config=generate_content_config
            )

            # Display streaming response and accumulate full text
            full_response = ""
            for chunk in stream:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response += chunk.text

            print()  # Add newline after streaming is complete
            ai_response = full_response if full_response else ""

            # Store both messages in database
            self.conversation_repo.add_message(session_id, "user", user_input)
            self.conversation_repo.add_message(session_id, "assistant", ai_response)

            # Generate session name if this is the first message in the session
            history = self.conversation_repo.get_conversation_history(session_id)
            if len(history) == 2:  # First user message + first AI response
                session_name = self.ai_client.generate_session_name(user_input, ai_response)
                if session_name:
                    self.conversation_repo.update_session_name(session_id, session_name)

            return ai_response

        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg