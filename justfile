default: run

# Run the application
@run:
  uv run main.py

# Install dependencies
@sync:
  uv sync

# Clean database
@clean:
	echo "Cleaning up database data..."
	rm -rf cs.db
