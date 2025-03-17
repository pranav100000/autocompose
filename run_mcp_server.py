"""
Script to run the MCP server for development.
"""
import os
import sys
from app.mcp import mcp

if __name__ == "__main__":
    print("Starting AutoCompose MCP Server...")
    print("Hit Ctrl+C to exit")
    
    try:
        # Run the MCP server
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down MCP server...")
        sys.exit(0)