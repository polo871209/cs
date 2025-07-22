"""Chat service for handling AI conversations"""

import sys
import uuid
from datetime import datetime
from typing import List

from google.genai import types
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

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

    def __init__(
        self, ai_client: GeminiClient, conversation_repo: ConversationRepository
    ):
        self.ai_client = ai_client
        self.conversation_repo = conversation_repo
        self.console = Console()

    def build_conversation_contents(
        self, session_id: str, user_input: str
    ) -> List[types.Content]:
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

    def get_session_token_count(self, session_id: str) -> int:
        """Calculate total token count for a session by approximating from text length"""
        history = self.conversation_repo.get_conversation_history(session_id)
        total_chars = 0
        
        for msg in history:
            total_chars += len(msg.get('content', ''))
        
        # Rough approximation: 1 token ≈ 4 characters for English text
        # This is a simplified estimate since we don't have exact token counts from history
        estimated_tokens = total_chars // 4
        return estimated_tokens

    def send_message(self, session_id: str, user_input: str) -> str:
        """Send message to AI and store in database"""
        contents = self.build_conversation_contents(session_id, user_input)

        # Configure response format
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            tools=[fetch_current_weather],
        )

        try:
            # Get AI response with streaming
            stream = self.ai_client.generate_content_stream(
                contents=contents, config=generate_content_config
            )

            # Check if we're in an interactive terminal
            is_tty = sys.stdout.isatty()
            
            # Initialize token counting
            total_tokens = 0
            input_tokens = 0
            output_tokens = 0

            if is_tty:
                # Use Rich Live for real-time markdown rendering
                full_response = ""

                with Live(
                    Markdown(""), console=self.console, refresh_per_second=4
                ) as live:
                    for chunk in stream:
                        if chunk.text:
                            full_response += chunk.text
                            # Update with live markdown rendering
                            live.update(Markdown(full_response))
                        
                        # Collect token usage if available
                        if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
                            usage = chunk.usage_metadata
                            if hasattr(usage, 'prompt_token_count'):
                                input_tokens = usage.prompt_token_count
                            if hasattr(usage, 'candidates_token_count'):
                                output_tokens = usage.candidates_token_count
                            if hasattr(usage, 'total_token_count'):
                                total_tokens = usage.total_token_count

                # Final check for empty response
                if not full_response.strip():
                    self.console.print("(No response received)")
            else:
                # Non-interactive: just stream normally
                full_response = ""
                for chunk in stream:
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                        full_response += chunk.text
                    
                    # Collect token usage if available
                    if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
                        usage = chunk.usage_metadata
                        if hasattr(usage, 'prompt_token_count'):
                            input_tokens = usage.prompt_token_count
                        if hasattr(usage, 'candidates_token_count'):
                            output_tokens = usage.candidates_token_count
                        if hasattr(usage, 'total_token_count'):
                            total_tokens = usage.total_token_count
                print()  # Final newline

            ai_response = full_response if full_response else ""

            # Store both messages in database
            self.conversation_repo.add_message(session_id, "user", user_input)
            self.conversation_repo.add_message(session_id, "assistant", ai_response)

            # Display token usage information
            if total_tokens > 0:
                # Get session total tokens
                session_total = self.get_session_token_count(session_id)
                token_info = f"📊 Tokens: {input_tokens} in + {output_tokens} out = {total_tokens} total | Session: {session_total}"
                if is_tty:
                    self.console.print(f"\n{token_info}", style="dim cyan")
                else:
                    print(f"\n{token_info}")

            # Generate session name if this is the first message in the session
            history = self.conversation_repo.get_conversation_history(session_id)
            if len(history) == 2:  # First user message + first AI response
                session_name = self.ai_client.generate_session_name(
                    user_input, ai_response
                )
                if session_name:
                    self.conversation_repo.update_session_name(session_id, session_name)

            return ai_response

        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
