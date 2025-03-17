#!/usr/bin/env python3
"""
Script to run a single MCP session for music generation.
This script uses the Model Context Protocol (MCP) to generate structured music descriptions.
"""
import sys
import json
import asyncio
import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up detailed logging
log_level = os.environ.get("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.debug("Logger initialized with level: %s", log_level)

# Check dependencies
required_packages = ['anthropic']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(package)
        logger.error(f"{package} package not installed.")

if missing_packages:
    logger.error(f"Missing required packages: {', '.join(missing_packages)}")
    logger.error(f"Please install with: pip install {' '.join(missing_packages)}")
    sys.exit(1)

async def run_mcp_session(description: str, output_path: str):
    """
    Run an MCP session to generate music from a description.
    This connects to our MCP server which provides music generation tools.

    Args:
        description: Text description of the music to generate
        output_path: Path to write the JSON result to
    """
    logger.debug(f"Starting MCP session for: {description[:100]}...")
    
    try:
        # Import our client
        from app.mcp.client import MCPClient
        logger.debug("Successfully imported MCPClient")
        
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            result = {
                "status": "error",
                "error": "ANTHROPIC_API_KEY not set",
                "music_description": {"error": "No API key", "title": "Error", "tempo": 120, "instruments": []}
            }
            with open(output_path, 'w') as f:
                json.dump(result, f)
            return
        
        # Extract tempo from description if specified
        tempo = None
        if "BPM" in description or "bpm" in description:
            import re
            tempo_match = re.search(r'(\d+)\s*(?:BPM|bpm)', description)
            if tempo_match:
                tempo = int(tempo_match.group(1))
                logger.debug(f"Extracted tempo from description: {tempo} BPM")
        
        # Initialize MCP client
        model = os.environ.get("MODEL_ID", "claude-3-7-sonnet-latest")
        server_port = int(os.environ.get("MCP_PORT", "5000"))
        server_host = os.environ.get("MCP_HOST", "localhost")
        logger.debug(f"Using model: {model}, connecting to MCP server at {server_host}:{server_port}")
        
        # Initialize MCPClient
        logger.debug("Initializing MCPClient...")
        client = MCPClient(
            model=model,
            api_key=api_key,
            temperature=0.7,
            max_tokens=4000,
            server_port=server_port,
            server_host=server_host
        )
        logger.debug("MCPClient initialized successfully")
        
        # Run the MCP session
        logger.debug("Running MCP session to generate music description")
        music_description = await client.run_session(description, tempo)
        logger.debug("MCP session completed successfully")
        
        # Check that it has the required fields
        required_fields = ["title", "tempo", "instruments"]
        missing_fields = [field for field in required_fields if field not in music_description]
        
        if missing_fields:
            logger.error(f"Missing required fields in music description: {missing_fields}")
            result = {
                "status": "error",
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "music_description": {
                    "title": music_description.get("title", "Error"),
                    "tempo": music_description.get("tempo", 120),
                    "instruments": music_description.get("instruments", [])
                }
            }
        else:
            # Success!
            logger.info(f"Successfully generated music description: {music_description['title']}")
            instrument_count = len(music_description.get("instruments", []))
            logger.info(f"Number of instruments: {instrument_count}")
            result = {
                "status": "success",
                "music_description": music_description
            }
            
    except Exception as e:
        logger.error(f"Error in MCP session: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        
        # Detailed error information
        import traceback
        detailed_traceback = traceback.format_exc()
        logger.debug("Detailed traceback:\n%s", detailed_traceback)
        
        result = {
            "status": "error",
            "error": f"MCP session error: {str(e)}",
            "detailed_error": detailed_traceback,
            "music_description": {"error": str(e), "title": "Error", "tempo": 120, "instruments": []}
        }
    
    # Write the result to the output file
    logger.debug("Writing result to output file: %s", output_path)
    with open(output_path, 'w') as f:
        json.dump(result, f)
    logger.debug("Output file written successfully")

async def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} 'music description' output_path.json")
        sys.exit(1)
    
    description = sys.argv[1]
    output_path = sys.argv[2]
    
    await run_mcp_session(description, output_path)

if __name__ == "__main__":
    asyncio.run(main())