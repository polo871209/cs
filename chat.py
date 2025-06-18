import os
import uuid
from datetime import datetime

from google import genai

from db import ConversationDB


class AIChat:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        self.db = ConversationDB()
        self.session_id = self.create_new_session()

    def create_new_session(self) -> str:
        """Create a new unique session ID"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        print(f"🆕 New session created: {session_id}")
        return session_id

    def format_conversation_context(self) -> str:
        """Get conversation history and format for API"""
        history = self.db.get_conversation_history(self.session_id)

        if not history:
            return ""

        context = "Previous conversation:\n"
        for msg in history:
            role = "Human" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"

        context += "\nCurrent conversation:\n"
        return context

    def send_message(self, user_input: str) -> str:
        """Send message to AI and store in database"""
        # Get conversation context
        context = self.format_conversation_context()

        # Prepare the full prompt with context
        full_prompt = context + f"Human: {user_input}\nAssistant:"

        try:
            # Get AI response
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt if context else user_input,
            )

            ai_response = response.text

            # Store both messages in database
            self.db.add_message(self.session_id, "user", user_input)
            self.db.add_message(self.session_id, "assistant", ai_response)

            return ai_response

        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def show_conversation_history(self):
        """Display current session's conversation history"""
        history = self.db.get_conversation_history(self.session_id)

        if not history:
            print("📝 No conversation history for this session.")
            return

        print(f"\n📋 Conversation History (Session: {self.session_id}):")
        print("-" * 60)
        for msg in history:
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            role_name = "You" if msg["role"] == "user" else "AI"
            print(f"{role_emoji} {role_name}: {msg['content']}")
            print(f"   ⏰ {msg['timestamp']}")
            print()

    def list_all_sessions(self):
        """Show all available sessions"""
        sessions = self.db.get_all_sessions()
        if not sessions:
            print("📝 No previous sessions found.")
            return

        print("\n📚 Available Sessions:")
        for i, session in enumerate(sessions, 1):
            print(f"{i}. {session}")

    def start_chat_loop(self):
        """Start the interactive chat loop"""
        print("🚀 AI Chat with Memory Started!")
        print(f"💾 Database: {self.db.db_path}")
        print(f"🆔 Session ID: {self.session_id}")
        print("\nCommands:")
        print("  /history - Show conversation history")
        print("  /sessions - List all sessions")
        print("  /new - Start new session")
        print("  /quit or /exit - Exit chat")
        print("-" * 60)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["/quit", "/exit"]:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == "/history":
                    self.show_conversation_history()
                    continue
                elif user_input.lower() == "/sessions":
                    self.list_all_sessions()
                    continue
                elif user_input.lower() == "/new":
                    self.session_id = self.create_new_session()
                    continue

                # Send message to AI
                print("🤖 AI: ", end="", flush=True)
                ai_response = self.send_message(user_input)
                print(ai_response)

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
