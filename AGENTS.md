# Agent Guidelines for CS Project

## Build/Lint/Test Commands
- **Run app**: `just` or `just run` or `uv run main.py`
- **Clean database**: `just clean`
- **Install dependencies**: `uv install` or `uv sync`
- **No specific test framework** - Check if tests exist before assuming pytest/unittest

## Code Style & Conventions

### Python Standards
- **Type checking**: Disabled in pyproject.toml (`typeCheckingMode = "off"`)
- **Type hints**: Use standard typing (e.g., `str | None`, `Dict[str, any]`)
- **Imports**: Standard library first, third-party, then local modules with blank lines between groups
- **Class structure**: Use dataclasses for data containers (`@dataclass`)

### Naming & Structure
- **Functions**: snake_case with descriptive docstrings
- **Classes**: PascalCase
- **Constants**: Use environment variables with `os.getenv()` for consistency
- **Database**: Use context managers for connections, proper error handling with try/except

### Error Handling
- Print user-friendly error messages with emoji prefixes (❌, ✅, 🚀)
- Use proper exception handling with specific exception types
- Validate inputs early and raise ValueError for invalid parameters
- Always close database connections properly using context managers