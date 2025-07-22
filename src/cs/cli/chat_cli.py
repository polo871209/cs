"""Command-line interface for the CS chat application"""

from ..chat import ChatApplication


class ChatCLI:
    """Command-line interface for the chat application"""
    
    def __init__(self):
        self.chat_app = ChatApplication()
    
    def show_conversation_history(self):
        """Display current session's conversation history"""
        history = self.chat_app.get_conversation_history()
        session_info = self.chat_app.conversation_repo.get_session_info(self.chat_app.current_session_id)

        if not history:
            print("📝 No conversation history for this session.")
            return

        session_display = session_info.session_name if session_info else self.chat_app.current_session_id
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
        sessions = self.chat_app.get_all_sessions()
        if not sessions:
            print("📝 No previous sessions found.")
            return

        print("\n📚 Available Sessions:")
        for i, session in enumerate(sessions, 1):
            print(f"{i}. {session.session_name}")

    def switch_session(self):
        """Allow user to switch to a different session"""
        sessions = self.chat_app.get_all_sessions()
        if not sessions:
            print("📝 No previous sessions found.")
            return

        # Show available sessions with current session marked
        print("\n📚 Available Sessions:")
        for i, session in enumerate(sessions, 1):
            current_marker = (
                " ← Current" if session.session_id == self.chat_app.current_session_id else ""
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
                if self.chat_app.switch_session(selected_session.session_id):
                    print(f"✅ Switched to session: '{selected_session.session_name}'")
                    print(f"🆔 Session ID: {selected_session.session_id}")

                    # Show recent conversation from this session
                    recent_history = self.chat_app.get_conversation_history(limit=3)
                    if recent_history:
                        print("\n📖 Recent conversation:")
                        for msg in recent_history[-3:]:
                            role_emoji = "👤" if msg["role"] == "user" else "🤖"
                            role_name = "You" if msg["role"] == "user" else "AI"
                            content = (
                                msg["content"][:100] + "..."
                                if len(msg["content"]) > 100
                                else msg["content"]
                            )
                            print(f"   {role_emoji} {role_name}: {content}")
                        print()
                else:
                    print("❌ Failed to switch to session.")
            else:
                print("❌ Invalid session number.")

        except ValueError:
            print("❌ Please enter a valid number.")
        except Exception as e:
            print(f"❌ Error switching session: {str(e)}")

    def show_current_session(self):
        """Show information about the current session"""
        session_info = self.chat_app.conversation_repo.get_session_info(self.chat_app.current_session_id)

        if not session_info:
            print("❌ Current session not found.")
            return

        print("\n📋 Current Session Information:")
        print("-" * 40)
        print(f"📝 Name: {session_info.session_name}")
        print(f"🆔 ID: {self.chat_app.current_session_id}")
        print(f"📅 Created: {session_info.created_at}")

        # Show message count
        history = self.chat_app.get_conversation_history()
        message_count = len(history)
        print(f"💬 Messages: {message_count}")

        if message_count > 0:
            print(f"⏰ Last activity: {history[-1]['timestamp']}")
        print()

    def start_chat_loop(self):
        """Start the interactive chat loop"""
        # Show initial session info
        session_info = self.chat_app.conversation_repo.get_session_info(self.chat_app.current_session_id)

        if not session_info:
            print("❌ Current session not found. Please create a new session first.")
            return

        print("🚀 AI Chat with Memory Started!")
        print(f"💾 Database: {self.chat_app.conversation_repo.db_path}")
        print(f"📝 Current Session: {session_info.session_name}")
        print(f"🆔 Session ID: {self.chat_app.current_session_id}")
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
                session_info = self.chat_app.conversation_repo.get_session_info(self.chat_app.current_session_id)

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
                        self.chat_app.create_new_session()
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
                            self.chat_app.clear_current_session()
                            print("🗑️ Session cleared!")
                            print("✅ Started fresh session")
                        else:
                            print("❌ Clear cancelled.")
                        continue

                # Send message to AI
                print("\n🤖 AI:")
                self.chat_app.send_message(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                break