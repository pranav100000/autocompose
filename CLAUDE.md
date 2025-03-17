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
- **Run MCP server**: `python run_mcp_server.py`
- **Test MCP server**: `mcp dev run_mcp_server.py`

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

## MCP Implementation Guidelines

### Correct Import Patterns
```python
# Server-side MCP
from mcp.server.fastmcp import FastMCP, Context

# Client-side MCP
from mcp.claude.client import ClaudeClient
```

### Creating MCP Tools
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AutoCompose")

@mcp.tool()
async def create_music_description(description: str, tempo: int = None) -> dict:
    """Tool documentation here"""
    # Implementation
    return result
```

### MCP Server Structure
- Tools are defined with the `@mcp.tool()` decorator
- Resources are defined with the `@mcp.resource()` decorator
- Prompts are defined with the `@mcp.prompt()` decorator
- Server is initialized with `FastMCP("ServerName")`
- Server is run with `mcp.run()`

### Notes on MCP Architecture
- MCP separates context provision from LLM interaction
- Three core primitives: Prompts, Resources, and Tools
- Strict schema typing through parameters
- Proper error handling through the MCP protocol

### Documentation Links
- [MCP Python SDK](https://pypi.org/project/mcp/)
- [MCP Specification](https://github.com/anthropics/model-context-protocol)