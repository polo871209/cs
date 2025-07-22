"""Command-line interface for the CS chat application"""

import getpass
from typing import Dict

from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from ..chat import ChatApplication


class ChatCLI:
    """Command-line interface for the chat application"""

    def __init__(self):
        self.chat_app = ChatApplication()
        self.console = Console()
        self.username = getpass.getuser()
        self.commands = self._register_commands()

    def _cmd_quit(self, args: list = None) -> bool:
        """Exit command"""
        self.console.print("👋 Goodbye!", style="cyan")
        return True  # Return True to exit main loop

    def _cmd_help(self, args: list = None) -> bool:
        """Show help command"""
        help_content = """
**🔧 Basic Commands**
- `/help` (`/?`, `/commands`) - Show all available commands
- `/quit` (`/exit`) - Exit the chat application

**💬 Session Management**
- `/new` (`/create`) - Create and switch to a new session
- `/current` (`/info`, `/session`) - Show current session information
- `/switch` (`/s`) - Switch to a different session
- `/sessions` (`/list`, `/ls`) - List all available sessions
- `/clear` (`/reset`) - Clear current session conversation

**📋 Conversation**
- `/history` (`/h`) - Show conversation history for current session
- `/tokens` (`/t`) - Show token usage for current session

💡 Any input not starting with '/' will be sent to the AI
        """

        self.console.print(Markdown(help_content))
        return False

    def _cmd_history(self, args: list = None) -> bool:
        """Show conversation history"""
        self.show_conversation_history()
        return False

    def _cmd_sessions(self, args: list = None) -> bool:
        """List all sessions"""
        self.list_all_sessions()
        return False

    def _cmd_tokens(self, args: list = None) -> bool:
        """Show token usage for current session"""
        session_id = self.chat_app.current_session_id
        estimated_tokens = self.chat_app.message_handler.get_session_token_count(
            session_id
        )

        session_info = self.chat_app.conversation_repo.get_session_info(session_id)
        session_name = session_info.session_name if session_info else session_id

        history = self.chat_app.get_conversation_history()
        message_count = len(history)

        tokens_content = f"""
**📊 Token Usage for Session**

**Session:** {session_name}  
**Messages:** {message_count}  
**Estimated Tokens:** ~{estimated_tokens}  

*Note: Token count is estimated based on text length (~4 chars per token)*
        """

        self.console.print(Markdown(tokens_content))
        return False

    def _cmd_sessions(self, args: list = None) -> bool:
        """List all sessions"""
        self.list_all_sessions()
        return False

    def _cmd_switch(self, args: list = None) -> bool:
        """Switch session"""
        self.switch_session()
        return False

    def _cmd_current(self, args: list = None) -> bool:
        """Show current session"""
        self.show_current_session()
        return False

    def _cmd_new(self, args: list = None) -> bool:
        """Create new session"""
        self.chat_app.create_new_session()
        self.console.print("✅ Now in new session", style="green")
        return False

    def _cmd_clear(self, args: list = None) -> bool:
        """Clear current session"""
        confirm = (
            input("⚠️ Are you sure you want to clear this session? (y/N): ")
            .strip()
            .lower()
        )
        if confirm in ["y", "yes"]:
            self.chat_app.clear_current_session()
            self.console.print("🗑️ Session cleared!", style="yellow")
            self.console.print("✅ Started fresh session", style="green")
        else:
            self.console.print("❌ Clear cancelled.", style="red")
        return False

    def _get_command_name(self, input_command: str) -> str | None:
        """Find command name from input, checking aliases"""
        for cmd_name, cmd_info in self.commands.items():
            if input_command == cmd_name:
                return cmd_name
            if input_command in cmd_info.get("aliases", []):
                return cmd_name
        return None

    def _register_commands(self) -> Dict[str, Dict[str, any]]:
        """Register all available commands with descriptions"""
        return {
            "quit": {
                "func": self._cmd_quit,
                "aliases": ["exit"],
                "description": "Exit the chat application",
                "usage": "/quit or /exit",
            },
            "help": {
                "func": self._cmd_help,
                "aliases": ["?", "commands"],
                "description": "Show all available commands",
                "usage": "/help",
            },
            "history": {
                "func": self._cmd_history,
                "aliases": ["h"],
                "description": "Show conversation history for current session",
                "usage": "/history",
            },
            "tokens": {
                "func": self._cmd_tokens,
                "aliases": ["t"],
                "description": "Show token usage for current session",
                "usage": "/tokens",
            },
            "sessions": {
                "func": self._cmd_sessions,
                "aliases": ["list", "ls"],
                "description": "List all available sessions",
                "usage": "/sessions",
            },
            "switch": {
                "func": self._cmd_switch,
                "aliases": ["s"],
                "description": "Switch to a different session",
                "usage": "/switch",
            },
            "current": {
                "func": self._cmd_current,
                "aliases": ["info", "session"],
                "description": "Show current session information",
                "usage": "/current",
            },
            "new": {
                "func": self._cmd_new,
                "aliases": ["create"],
                "description": "Create and switch to a new session",
                "usage": "/new",
            },
            "clear": {
                "func": self._cmd_clear,
                "aliases": ["reset"],
                "description": "Clear current session conversation",
                "usage": "/clear",
            },
        }

    def handle_command(self, user_input: str) -> bool:
        """Handle command input. Returns True if should exit."""
        if not user_input.startswith("/"):
            return False  # Not a command

        # Parse command and arguments
        parts = user_input[1:].split()
        if not parts:
            self._cmd_help()
            return False

        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        # Find and execute command
        cmd_name = self._get_command_name(command)
        if cmd_name:
            cmd_func = self.commands[cmd_name]["func"]
            return cmd_func(args)
        else:
            # Unknown command - show help
            self.console.print(f"❌ Unknown command: '/{command}'", style="red")
            self._cmd_help()
            return False

    def show_conversation_history(self):
        """Display current session's conversation history"""
        history = self.chat_app.get_conversation_history()
        session_info = self.chat_app.conversation_repo.get_session_info(
            self.chat_app.current_session_id
        )

        if not history:
            self.console.print(
                "📝 No conversation history for this session.", style="yellow"
            )
            return

        session_display = (
            session_info.session_name
            if session_info
            else self.chat_app.current_session_id
        )

        # Create compact markdown content for conversation history
        markdown_content = f"**📋 History: {session_display}**\n\n"

        for msg in history:
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            role_name = f"**{self.username}**" if msg["role"] == "user" else "**AI**"
            markdown_content += f"{role_emoji} {role_name}: {msg['content']}\n"
            markdown_content += f"*{msg['timestamp']}*\n\n"

        self.console.print(Markdown(markdown_content))

    def list_all_sessions(self):
        """Show all available sessions"""
        sessions = self.chat_app.get_all_sessions()
        if not sessions:
            self.console.print("📝 No previous sessions found.", style="yellow")
            return

        # Create a compact table for sessions
        table = Table(
            title="📚 Sessions",
            show_header=True,
            header_style="bold cyan",
            title_justify="left",
            padding=(0, 1),
        )
        table.add_column("#", style="dim", width=2, no_wrap=True)
        table.add_column("Name", style="white", min_width=15)
        table.add_column("Created", style="green", width=10, no_wrap=True)
        table.add_column("Msgs", style="yellow", width=4, no_wrap=True)

        for i, session in enumerate(sessions, 1):
            created_date = (
                session.created_at.split()[0] if session.created_at else "Unknown"
            )
            table.add_row(
                str(i),
                session.session_name,
                created_date,
                str(session.message_count or 0),
            )

        self.console.print(table)

    def switch_session(self):
        """Allow user to switch to a different session"""
        sessions = self.chat_app.get_all_sessions()
        if not sessions:
            self.console.print("📝 No previous sessions found.", style="yellow")
            return

        # Create a compact table for session selection
        table = Table(show_header=True, header_style="bold cyan", padding=(0, 1))
        table.add_column("#", style="dim", width=2, no_wrap=True)
        table.add_column("Name", style="white", min_width=15)
        table.add_column("Status", style="green", width=8, no_wrap=True)
        table.add_column("Msgs", style="yellow", width=4, no_wrap=True)

        for i, session in enumerate(sessions, 1):
            status = (
                "Current"
                if session.session_id == self.chat_app.current_session_id
                else ""
            )
            table.add_row(
                str(i), session.session_name, status, str(session.message_count or 0)
            )

        self.console.print(table)

        try:
            choice = input(
                "\nEnter session number to switch (or press Enter to cancel): "
            ).strip()
            if not choice:
                self.console.print("❌ Switch cancelled.", style="red")
                return

            session_index = int(choice) - 1
            if 0 <= session_index < len(sessions):
                selected_session = sessions[session_index]
                if self.chat_app.switch_session(selected_session.session_id):
                    self.console.print(
                        f"✅ Switched to: {selected_session.session_name}",
                        style="green",
                    )

                    # Show recent conversation from this session
                    recent_history = self.chat_app.get_conversation_history(limit=3)
                    if recent_history:
                        recent_content = "\n**📖 Recent conversation:**\n\n"
                        for msg in recent_history[-3:]:
                            role_emoji = "👤" if msg["role"] == "user" else "🤖"
                            role_name = (
                                f"**{self.username}**"
                                if msg["role"] == "user"
                                else "**AI**"
                            )
                            content = (
                                msg["content"][:80] + "..."
                                if len(msg["content"]) > 80
                                else msg["content"]
                            )
                            recent_content += f"{role_emoji} {role_name}: {content}\n"

                        self.console.print(Markdown(recent_content))
                else:
                    self.console.print("❌ Failed to switch to session.", style="red")
            else:
                self.console.print("❌ Invalid session number.", style="red")

        except ValueError:
            self.console.print("❌ Please enter a valid number.", style="red")
        except Exception as e:
            self.console.print(f"❌ Error switching session: {str(e)}", style="red")

    def show_current_session(self):
        """Show information about the current session"""
        session_info = self.chat_app.conversation_repo.get_session_info(
            self.chat_app.current_session_id
        )

        if not session_info:
            self.console.print("❌ Current session not found.", style="red")
            return

        # Get message count
        history = self.chat_app.get_conversation_history()
        message_count = len(history)
        last_activity = (
            history[-1]["timestamp"] if message_count > 0 else "No messages yet"
        )

        # Create session info as compact markdown
        session_content = f"""
**📋 Current Session**
📝 {session_info.session_name}  
🆔 `{self.chat_app.current_session_id}`  
📅 {session_info.created_at} • 💬 {message_count} messages  
⏰ {last_activity}
        """

        self.console.print(Markdown(session_content))

    def start_chat_loop(self):
        """Start the interactive chat loop"""
        # Show initial session info
        session_info = self.chat_app.conversation_repo.get_session_info(
            self.chat_app.current_session_id
        )

        if not session_info:
            self.console.print(
                "❌ Current session not found. Please create a new session first.",
                style="red",
            )
            return

        # Create compact welcome message
        welcome_content = f"""
**🚀 AI Chat Started**
💾 Database: `{self.chat_app.conversation_repo.db_path}`  
📝 Session: {session_info.session_name}  
💡 Type `/help` for commands
        """

        self.console.print(Markdown(welcome_content))
        self.console.print("─" * 50, style="dim")

        while True:
            try:
                # Show current session name in prompt
                session_info = self.chat_app.conversation_repo.get_session_info(
                    self.chat_app.current_session_id
                )

                if not session_info:
                    self.console.print(
                        "❌ Unexpected error: Session not found", style="red"
                    )
                    break

                user_input = input(f"\n👤 {self.username}: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    should_exit = self.handle_command(user_input)
                    if should_exit:
                        break
                    continue

                # Send message to AI
                self.console.print("\n🤖 AI:", style="cyan bold")
                self.chat_app.send_message(user_input)

            except KeyboardInterrupt:
                self.console.print("\n\n👋 Chat interrupted. Goodbye!", style="cyan")
                break
            except Exception as e:
                self.console.print(f"❌ Error: {str(e)}", style="red")
                break
