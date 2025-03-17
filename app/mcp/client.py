import os
import sys
import json
import traceback
import logging
import asyncio
import subprocess
from typing import Dict, List, Optional, Any, Callable
from anthropic import Anthropic

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.debug("----- MCP CLIENT INITIALIZATION -----")
logger.debug("Python version: %s", sys.version)
logger.debug("Python path: %s", sys.path)
logger.debug("Current working directory: %s", os.getcwd())

class MCPClient:
    """
    Client for generating structured music descriptions by connecting to an MCP server.
    This implementation follows the official MCP client pattern to connect to our local
    MCP server that exposes music generation tools.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "claude-3-7-sonnet-latest",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        server_port: int = 5000,
        server_host: str = "localhost"
    ):
        """
        Initialize the MCP client.
        
        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY environment variable.
            model: Model to use.
            temperature: Temperature for generation (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.
            server_port: Port where the MCP server is running
            server_host: Host where the MCP server is running
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        # Store configuration
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.server_host = server_host
        self.server_port = server_port
        
        # Initialize Anthropic client as backup
        self.client = Anthropic(api_key=self.api_key)
        logger.debug("Initialized MCPClient")
    
    async def run_session(self, description: str, tempo: Optional[int] = None) -> Dict[str, Any]:
        """
        Run a session to generate a structured music description by connecting
        to the MCP server and using its tools.
        
        Args:
            description: Text description of the music to generate
            tempo: Optional tempo in BPM
            
        Returns:
            Structured music description as a dictionary
        """
        logger.debug(f"Starting music generation for: {description[:100]}...")
        
        try:
            # Import MCP client modules
            from mcp import ClientSession
            from mcp.client.http import http_client
            
            # Check if the server is running
            server_running = await self._check_server_running()
            if not server_running:
                logger.warning("MCP server not running, starting it now...")
                await self._start_server()
            
            # Set up the client connection to the MCP server
            logger.debug(f"Connecting to MCP server at {self.server_host}:{self.server_port}")
            async with http_client(f"http://{self.server_host}:{self.server_port}") as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # List available tools to make sure our connection works
                    tools = await session.list_tools()
                    logger.debug(f"Available tools: {[tool.name for tool in tools]}")
                    
                    # Check if our required tools are available
                    if not any(tool.name == "create_music_description" for tool in tools):
                        raise ValueError("Required tool 'create_music_description' not found on MCP server")
                    
                    # Prepare arguments for the create_music_description tool
                    args = {"description": description}
                    if tempo:
                        args["tempo"] = tempo
                    
                    # Call the tool to generate the music description
                    logger.debug(f"Calling create_music_description tool with args: {args}")
                    result = await session.call_tool("create_music_description", arguments=args)
                    
                    # The tool result should be our music description
                    if not result or not isinstance(result, dict):
                        raise ValueError(f"Unexpected result from create_music_description tool: {result}")
                    
                    music_description = result
                    logger.debug("Successfully generated music description through MCP server")
                    return music_description
        
        except Exception as e:
            logger.error(f"Error in MCP session: {str(e)}")
            logger.debug(traceback.format_exc())
            
            # Fallback to direct Anthropic API if MCP server fails
            logger.warning("Falling back to direct Anthropic API due to MCP server error")
            return await self._fallback_direct_api(description, tempo)
    
    async def _check_server_running(self) -> bool:
        """Check if the MCP server is running by attempting to connect to it."""
        import socket
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((self.server_host, self.server_port))
            s.close()
            return result == 0
        except:
            return False
    
    async def _start_server(self) -> None:
        """Start the MCP server as a background process."""
        try:
            script_path = os.path.join(os.getcwd(), "run_mcp_server.py")
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for the server to start
            await asyncio.sleep(2)
            logger.debug("Started MCP server as background process")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def _fallback_direct_api(self, description: str, tempo: Optional[int] = None) -> Dict[str, Any]:
        """Fallback method to generate music directly through the Anthropic API."""
        logger.debug("Using direct Anthropic API fallback")
        
        # Create a system prompt that enforces JSON output
        system_prompt = """You are a music composition assistant that generates MIDI music based on text descriptions.

YOU MUST RETURN A VALID JSON OBJECT WITH THE FOLLOWING STRUCTURE:
{
  "title": "Title of the composition",
  "tempo": 120,
  "key": "C major",
  "time_signature": [4, 4],
  "instruments": [
    {
      "program": 0,
      "name": "Piano",
      "soundfont_name": "Grand Piano",
      "channel": 0,
      "patterns": [
        {
          "type": "melody",
          "notes": [
            {"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80}
          ]
        }
      ]
    }
  ]
}

YOUR ENTIRE RESPONSE MUST BE ONLY THIS JSON - NO EXPLANATION TEXT, NO MARKDOWN.
"""

        # Create a user prompt for the music description
        user_prompt = f"""Create a detailed music composition based on this description:

{description}

{f"Use a tempo of {tempo} BPM." if tempo else ""}

Each instrument should have appropriate notes, rhythms, and dynamics based on the description.
Be creative with instrument selection and musical patterns to match the requested style."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Extract the response text
            response_text = response.content[0].text.strip()
            
            # Parse the JSON
            try:
                music_description = json.loads(response_text)
                logger.debug("Successfully parsed JSON fallback response")
                return music_description
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON fallback response: {e}")
                # Try to extract JSON with regex as a last resort
                import re
                json_match = re.search(r'(\{[\s\S]*\})', response_text)
                if json_match:
                    json_text = json_match.group(1)
                    music_description = json.loads(json_text)
                    return music_description
                else:
                    raise ValueError("Could not parse JSON from response")
                
        except Exception as e:
            logger.error(f"Fallback API error: {str(e)}")
            # Return a minimal valid response
            return {
                "title": f"Music inspired by: {description[:30]}",
                "tempo": tempo or 120,
                "key": "C minor",
                "time_signature": [4, 4],
                "instruments": []
            }