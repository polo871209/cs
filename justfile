default: run

@run:
  uv run main.py

@clean:
	echo "Cleaning up database data..."
	rm -rf cs.db
