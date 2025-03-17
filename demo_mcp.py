#!/usr/bin/env python3
"""
Demo script for AutoCompose MCP server.

This script runs the MCP server and provides a simple interface
to test music generation.
"""
import os
import sys
import asyncio
import logging
from app.mcp import mcp
from app.services.instruments import get_all_soundfonts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autocompose.demo")

async def main():
    """Run the demo."""
    # Print banner
    print("=" * 60)
    print("AutoCompose MCP Demo")
    print("=" * 60)
    
    # Check for soundfonts
    soundfonts = get_all_soundfonts()
    print(f"Found {len(soundfonts)} soundfont files")
    
    print("\nAvailable commands:")
    print("  run     - Start the MCP server")
    print("  inspect - Use 'mcp dev' to inspect the server")
    print("  exit    - Exit the demo")
    
    while True:
        command = input("\nCommand: ").strip().lower()
        
        if command == "exit":
            print("Exiting...")
            break
        elif command == "run":
            print("\nStarting MCP server...")
            print("Press Ctrl+C to stop")
            try:
                # Run the MCP server
                mcp.run()
            except KeyboardInterrupt:
                print("\nMCP server stopped")
        elif command == "inspect":
            # Run the MCP inspector
            os.system("mcp dev demo_mcp.py")
        else:
            print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())