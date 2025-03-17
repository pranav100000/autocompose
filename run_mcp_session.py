#!/usr/bin/env python3
"""
Script to run a single MCP session for music generation.
"""
import sys
import json
import asyncio
import os
import logging
import random
from typing import Dict, List, Any
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

# Import Anthropic client
try:
    from anthropic import Anthropic
except ImportError:
    logger.error("Anthropic package not installed. Please run: pip install anthropic")
    sys.exit(1)

async def run_mcp_session(description: str, output_path: str):
    """
    Run an MCP session to generate music from a description.
    This uses the proper MCP framework to ensure structured output.

    Args:
        description: Text description of the music to generate
        output_path: Path to write the JSON result to
    """
    logger.debug(f"Starting MCP session for: {description[:100]}...")
    
    # Import MCP related modules
    try:
        # We import these here to avoid circular imports and to keep the script standalone
        # Print detailed information about the MCP module and environment
        logger.debug("Python path: %s", sys.path)
        logger.debug("Current working directory: %s", os.getcwd())
        
        try:
            # Check if mcp package exists
            import mcp
            logger.debug("mcp package exists. mcp.__file__: %s", mcp.__file__)
            logger.debug("mcp package contents: %s", dir(mcp))
            
            # Check mcp version
            try:
                logger.debug("mcp version: %s", mcp.__version__)
            except AttributeError:
                logger.debug("mcp.__version__ not available")
                
            # Check if the fastmcp module exists
            try:
                import mcp.server.fastmcp
                logger.debug("mcp.server.fastmcp exists. Contents: %s", dir(mcp.server.fastmcp))
            except ImportError as e:
                logger.error("fastmcp module not found: %s", e)
        except ImportError as e:
            logger.error("mcp module not found: %s", e)
        
        # Try importing our client
        from app.mcp.client import MCPClient
        logger.debug("Successfully imported MCPClient")
        
    except ImportError as e:
        detailed_error = f"Failed to import required MCP modules: {str(e)}"
        logger.error(detailed_error)
        logger.error("Stack trace:", exc_info=True)
        
        # Check pip installations
        try:
            import subprocess
            pip_list = subprocess.check_output([sys.executable, "-m", "pip", "list"]).decode()
            logger.debug("Installed packages:\n%s", pip_list)
        except Exception as pip_error:
            logger.error("Error checking pip installations: %s", pip_error)
        
        result = {
            "status": "error",
            "error": detailed_error,
            "music_description": {"error": "MCP import error - missing required MCP packages", "title": "Error", "tempo": 120, "instruments": []}
        }
        with open(output_path, 'w') as f:
            json.dump(result, f)
        return
    
    try:
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
        
        # Initialize MCP client
        model = os.environ.get("MODEL_ID", "claude-3-7-sonnet-latest")
        logger.debug(f"Using model: {model}")
        
        # Extract tempo from description if specified
        tempo = None
        if "BPM" in description or "bpm" in description:
            import re
            tempo_match = re.search(r'(\d+)\s*(?:BPM|bpm)', description)
            if tempo_match:
                tempo = int(tempo_match.group(1))
                logger.debug(f"Extracted tempo from description: {tempo} BPM")
        
        # Initialize MCP client with detailed logging
        logger.debug("Initializing MCPClient...")
        client = MCPClient(
            model=model,
            api_key=api_key,
            temperature=0.7,
            max_tokens=4000
        )
        logger.debug("MCPClient initialized successfully")
        
        # Run the MCP session using the proper tool-based approach
        logger.debug("Running MCP session with create_music_description tool")
        # Trace the methods being called
        logger.debug("client type: %s", type(client))
        logger.debug("client methods: %s", [m for m in dir(client) if not m.startswith('_')])
        
        music_description = await client.run_session(description, tempo)
        logger.debug("MCP session completed with result type: %s", type(music_description))
        
        # Check that it has the required fields
        required_fields = ["title", "tempo", "instruments"]
        missing_fields = [field for field in required_fields if field not in music_description]
        
        if missing_fields:
            logger.error(f"Missing required fields in music description: {missing_fields}")
            logger.debug(f"music_description keys: {music_description.keys() if hasattr(music_description, 'keys') else 'not a dict'}")
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