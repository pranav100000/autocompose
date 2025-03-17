# AutoCompose Development Guide

## Commands
- **Run server**: `uvicorn app.main:app --reload`
- **Install dependencies**: `uv pip install -r requirements.txt`
- **Add dependency**: `uv pip install package_name`
- **Lint code**: `ruff check app tests`
- **Type check**: `mypy app tests`
- **Format code**: `black app tests`
- **Run all tests**: `pytest tests/`
- **Run a single test**: `pytest tests/path/to/test_file.py::test_function_name -v`

## Code Style Guidelines
- **Imports**: Group imports: stdlib, third-party, local. Sort alphabetically within groups.
- **Formatting**: Use Black with default settings; 88 character line length.
- **Types**: Use type hints for all function parameters and return values.
- **Naming**:
  - Classes: PascalCase
  - Functions/variables: snake_case
  - Constants: UPPER_SNAKE_CASE
- **Error Handling**: Use specific exceptions; include context in error messages.
- **Documentation**: Docstrings for modules, classes, and functions (Google style).
- **API Design**: RESTful principles; consistent response structures.
- **Testing**: Use pytest; aim for >80% coverage; mock external services.