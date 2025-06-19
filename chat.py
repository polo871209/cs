import os
import uuid
from datetime import datetime

from google import genai
from google.genai import types

from db.conversation import ConversationDB
from tools.weather import fetch_current_weather


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
        # Create session in database
        self.db.create_session(session_id)
        print(f"🆕 New session created: {session_id}")
        return session_id

    def generate_session_name(self, user_input: str, ai_response: str) -> str:
        """Generate a session name based on the first conversation"""
        try:
            # Ensure inputs are not None
            if not user_input or not ai_response:
                return "New Conversation"

            # Create a prompt to generate a short summary
            summary_prompt = f"""Based on this conversation, create a short 3-5 word title:
User: {user_input}
AI: {ai_response}

Generate only a concise title without quotes or extra text."""

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=summary_prompt),
                    ],
                )
            ]

            config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=config,
            )

            # Clean up the response
            if response and hasattr(response, "text") and response.text:
                session_name = response.text.strip().replace('"', "").replace("'", "")
                # Ensure we have a valid string
                if not session_name or len(session_name.strip()) == 0:
                    session_name = "New Conversation"
            else:
                session_name = "New Conversation"

            # Limit to reasonable length
            if len(session_name) > 50:
                session_name = session_name[:47] + "..."

            return session_name

        except Exception as e:
            print(f"⚠️ Could not generate session name: {e}")
            # Fallback to first few words of user input
            if user_input:
                words = user_input.split()[:3]
                return " ".join(words) + ("..." if len(user_input.split()) > 3 else "")
            else:
                return "New Conversation"

    def build_conversation_contents(self, user_input: str) -> list:
        """Build conversation contents using genai types structure"""
        history = self.db.get_conversation_history(self.session_id)

        contents = []

        # Add conversation history
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part.from_text(text=msg["content"]),
                    ],
                )
            )

        # Add current user input
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=user_input),
                ],
            )
        )

        return contents

    def send_message(self, user_input: str):
        """Send message to AI and store in database"""
        # Build conversation contents with proper structure
        contents = self.build_conversation_contents(user_input)

        # Configure response format
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            # https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview
            tools=[fetch_current_weather],
        )

        try:
            # Get AI response with streaming
            stream = self.client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=contents,
                config=generate_content_config,
            )

            # Display streaming response and accumulate full text
            full_response = ""
            for chunk in stream:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response += chunk.text

            print()  # Add newline after streaming is complete

            # Use accumulated response as ai_response
            ai_response = full_response if full_response else ""

            if not ai_response:
                ai_response = ""

            # Store both messages in database
            self.db.add_message(self.session_id, "user", user_input)
            self.db.add_message(self.session_id, "assistant", ai_response)

            # Generate session name if this is the first message in the session
            history = self.db.get_conversation_history(self.session_id)
            if len(history) == 2:  # First user message + first AI response
                session_name = self.generate_session_name(user_input, ai_response)
                if session_name:  # Only update if we got a valid name
                    self.db.update_session_name(self.session_id, session_name)

        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def show_conversation_history(self):
        """Display current session's conversation history"""
        history = self.db.get_conversation_history(self.session_id)
        session_info = self.db.get_session_info(self.session_id)

        if not history:
            print("📝 No conversation history for this session.")
            return

        session_display = session_info.session_name if session_info else self.session_id
        print(f"\n📋 Conversation History: {session_display}")
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
            print(f"{i}. {session.session_name}")

    def switch_session(self):
        """Allow user to switch to a different session"""
        sessions = self.db.get_all_sessions()
        if not sessions:
            print("📝 No previous sessions found.")
            return

        # Show available sessions with current session marked
        print("\n📚 Available Sessions:")
        for i, session in enumerate(sessions, 1):
            current_marker = (
                " ← Current" if session.session_name == self.session_id else ""
            )
            print(f"{i}. {session.session_name}{current_marker}")

        try:
            choice = input(
                "\nEnter session number to switch (or press Enter to cancel): "
            ).strip()
            if not choice:
                print("❌ Switch cancelled.")
                return

            session_index = int(choice) - 1
            if 0 <= session_index < len(sessions):
                selected_session = sessions[session_index]
                self.session_id = selected_session.session_id

                # Show session info
                session_name = selected_session.session_name
                print(f"✅ Switched to session: '{session_name}'")
                print(f"🆔 Session ID: {self.session_id}")

                # Show recent conversation from this session
                recent_history = self.db.get_conversation_history(
                    self.session_id, limit=3
                )
                if recent_history:
                    print("\n📖 Recent conversation:")
                    for msg in recent_history[-3:]:  # Last 3 messages
                        role_emoji = "👤" if msg["role"] == "user" else "🤖"
                        role_name = "You" if msg["role"] == "user" else "AI"
                        # Truncate long messages for preview
                        content = (
                            msg["content"][:100] + "..."
                            if len(msg["content"]) > 100
                            else msg["content"]
                        )
                        print(f"   {role_emoji} {role_name}: {content}")
                    print()
            else:
                print("❌ Invalid session number.")

        except ValueError:
            print("❌ Please enter a valid number.")
        except Exception as e:
            print(f"❌ Error switching session: {str(e)}")

    def show_current_session(self):
        """Show information about the current session"""
        session_info = self.db.get_session_info(self.session_id)

        if not session_info:
            print("❌ Current session not found.")
            return

        print("\n📋 Current Session Information:")
        print("-" * 40)
        print(f"📝 Name: {session_info.session_name}")
        print(f"🆔 ID: {self.session_id}")
        print(f"📅 Created: {session_info.created_at}")

        # Show message count
        history = self.db.get_conversation_history(self.session_id)
        message_count = len(history)
        print(f"💬 Messages: {message_count}")

        if message_count > 0:
            print(f"⏰ Last activity: {history[-1]['timestamp']}")
        print()

    def start_chat_loop(self):
        """Start the interactive chat loop"""
        # Show initial session info
        session_info = self.db.get_session_info(self.session_id)

        if not session_info:
            print("❌ Current session not found. Please create a new session first.")
            return

        print("🚀 AI Chat with Memory Started!")
        print(f"💾 Database: {self.db.db_path}")
        print(f"📝 Current Session: {session_info.session_name}")
        print(f"🆔 Session ID: {self.session_id}")
        print("\nCommands:")
        print("  /history - Show conversation history")
        print("  /sessions - List all sessions")
        print("  /switch - Switch to different session")
        print("  /current - Show current session info")
        print("  /new - Start new session")
        print("  /clear - Clear current session")
        print("  /quit or /exit - Exit chat")
        print("-" * 60)

        while True:
            try:
                # Show current session name in prompt
                session_info = self.db.get_session_info(self.session_id)

                if not session_info:
                    print("❌ Unexpected error: Session not found")
                    break

                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                match user_input.lower():
                    case "/quit" | "/exit":
                        print("👋 Goodbye!")
                        break
                    case "/history":
                        self.show_conversation_history()
                        continue
                    case "/sessions":
                        self.list_all_sessions()
                        continue
                    case "/switch":
                        self.switch_session()
                        continue
                    case "/current":
                        self.show_current_session()
                        continue
                    case "/new":
                        self.session_id = self.create_new_session()
                        print("✅ Now in new session")
                        continue
                    case "/clear":
                        confirm = (
                            input(
                                "⚠️ Are you sure you want to clear this session? (y/N): "
                            )
                            .strip()
                            .lower()
                        )
                        if confirm in ["y", "yes"]:
                            self.db.clear_session(self.session_id)
                            print("🗑️ Session cleared!")
                            # Create a new session
                            self.session_id = self.create_new_session()
                            print("✅ Started fresh session")
                        else:
                            print("❌ Clear cancelled.")
                        continue

                # Send message to AI
                print("🤖 AI: ", end="", flush=True)
                self.send_message(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                break
