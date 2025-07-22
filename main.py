"""Main entry point for the CS chat application"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from cs.cli import ChatCLI
from cs.config import settings


def main():
    """Main entry point"""
    try:
        # Validate configuration
        settings.validate()
        
        # Start the CLI application
        cli = ChatCLI()
        cli.start_chat_loop()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please set the required environment variables.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()