# Agent Guidelines for CS Project

## Project Structure (Modern Python Layout)
- **Source code**: `src/cs/` - All application code in importable package
- **Entry point**: `main.py` or `uv run main.py`
- **Tests**: No test directory currently exists - create `tests/` with pytest structure if needed
- **Database**: SQLite database at `cs.db` in project root

## Build/Lint/Test Commands
- **Run app**: `just run` or `uv run main.py`
- **Install**: `uv sync` (preferred) or `uv install`
- **Test all**: Create tests dir first, then `uv run python -m pytest tests/ -v`
- **Test single**: `uv run python -m pytest tests/unit/test_file.py::test_function -v`
- **Lint**: `uv run ruff check src/` (no ruff config found - uses defaults)
- **Format**: `uv run ruff format src/`
- **Type check**: `uv run pyright src/` (typeCheckingMode=off in pyproject.toml)
- **Clean database**: `just clean` (removes cs.db file)

## Code Style & Conventions

### Architecture Patterns
- **Repository Pattern**: Database operations in `src/cs/database/repositories/`
- **Dependency Injection**: Pass dependencies to constructors, avoid globals
- **Service Layer**: Business logic in `src/cs/chat/services.py`
- **Interface Segregation**: Use abstract base classes (`src/cs/tools/base_tool.py`)

### Python Standards
- **Package structure**: Use `src/` layout with proper `__init__.py` files
- **Type hints**: Use modern syntax (`str | None`) and `Optional[str]` from typing - Python 3.13+
- **Imports**: Standard imports (not relative) - import from `src.cs.module`
- **Models**: Dataclasses in `src/cs/database/models/entities.py` with docstrings
- **Line length**: Default ruff settings (88 characters)

### Naming & Organization
- **Modules**: snake_case.py (e.g., `chat_app.py`, `gemini_client.py`)
- **Classes**: PascalCase (e.g., `ChatApplication`, `SessionManager`)
- **Functions/vars**: snake_case with descriptive names
- **Constants**: Use `src/cs/config/settings.py` for environment variables

### Error Handling & Database
- **Context managers**: Always use for database connections (`with self.get_connection()`)
- **Error messages**: User-friendly with emoji prefixes (❌, ✅, 🚀)
- **Validation**: Early input validation with specific exceptions
- **Foreign keys**: Enable with `PRAGMA foreign_keys = ON`

### File Organization
- **Single responsibility**: One main class per file
- **Clear imports**: Export public API in `__init__.py` files
- **Documentation**: Docstrings for all public methods
- **Configuration**: Centralized in `src/cs/config/settings.py`