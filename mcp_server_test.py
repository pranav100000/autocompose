#!/usr/bin/env python
"""
Test file for a bare-bones MCP server.
"""
from mcp.server.fastmcp import FastMCP

# Create a minimal MCP server
mcp = FastMCP("Test")

# Add a simple tool
@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

# Add a simple resource
@mcp.resource("test://greeting")
def get_greeting() -> str:
    """Get a greeting message."""
    return "Welcome to the test MCP server!"

if __name__ == "__main__":
    print("Starting MCP server...")
    print("Use ctrl+c to exit")
    mcp.run()