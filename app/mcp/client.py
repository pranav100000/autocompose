import os
import sys
import json
import traceback
import logging
from typing import Dict, List, Optional, Any, Callable
from anthropic import Anthropic
from mcp.server.fastmcp import FastMCP, Context

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

# Check for MCP package and show exact versions
try:
    import pkg_resources
    logger.debug("INSTALLED PACKAGES:")
    for package in pkg_resources.working_set:
        if package.project_name in ['mcp', 'fastmcp', 'anthropic']:
            logger.debug("  %s: %s - %s", package.project_name, package.version, package.location)
except Exception as e:
    logger.error("Error listing packages: %s", e)

# First, check if we can import the base MCP module
logger.debug("CHECKING MCP MODULES:")
try:
    import mcp
    logger.debug("Basic mcp import successful")
    logger.debug("  mcp.__file__: %s", mcp.__file__)
    logger.debug("  mcp contents: %s", dir(mcp))
    
    # Check if specific MCP classes we need are available
    try:
        if hasattr(mcp, 'MCP'):
            logger.debug("  mcp.MCP exists")
        else:
            logger.debug("  mcp.MCP doesn't exist - wrong mcp package?")
            
        # Try importing specific modules we need
        modules_to_check = [
            'mcp.Tool', 'mcp.Parameter', 'mcp.MCPStore', 'mcp.MCPConfig', 
            'mcp.Message', 'mcp.claude.client', 'mcp.server.fastmcp'
        ]
        
        for module_path in modules_to_check:
            try:
                logger.debug("  Checking %s...", module_path)
                parts = module_path.split('.')
                module = __import__(parts[0])
                for part in parts[1:]:
                    module = getattr(module, part)
                logger.debug("  ✓ %s exists", module_path)
            except (ImportError, AttributeError) as e:
                logger.error("  ✗ %s missing: %s", module_path, e)
    
    except Exception as inner_e:
        logger.error("Error checking MCP components: %s", inner_e)
        logger.debug(traceback.format_exc())
        
except ImportError as e:
    logger.error("mcp package not found: %s", e)
    
logger = logging.getLogger(__name__)

class MCPClient:
    """
    Client for generating structured music descriptions using the Anthropic API.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "claude-3-7-sonnet-latest",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        Initialize the client.
        
        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY environment variable.
            model: Model to use.
            temperature: Temperature for generation (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        # Store configuration
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize Anthropic client directly
        self.client = Anthropic(api_key=self.api_key)
        logger.debug("Initialized Anthropic client directly")
    
    async def run_session(self, description: str, tempo: Optional[int] = None) -> Dict[str, Any]:
        """
        Run a session to generate a structured music description.
        Uses a strong system prompt to enforce JSON output format.
        
        Args:
            description: Text description of the music to generate
            tempo: Optional tempo in BPM
            
        Returns:
            Structured music description as a dictionary
        """
        logger.debug(f"Starting music generation for: {description[:100]}...")
        
        # Create a clear system prompt that enforces JSON output
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

MIDI Technical Guidelines:
- MIDI pitches: Middle C = 60, C4 = 60, C5 = 72, etc. (12 semitones per octave)
- Start times are in beats (e.g., 0.0, 1.0, 2.5)
- Durations are in beats (e.g., 0.5 = eighth note at 4/4, 1.0 = quarter note)
- Velocities: 1-127, with 64-100 being typical (127 = loudest)

General MIDI Program Numbers:
- Piano: 0-7 (0 = Acoustic Grand)
- Bass: 32-39 (33 = Electric Bass)
- Guitar: 24-31 (24 = Nylon, 25 = Steel, 30 = Distortion)
- Strings: 40-47 (48-51 for ensembles)
- Brass: 56-63
- Percussion: Use channel 9 with program = "percussion"
  - Note values are defined in GM drum map (36 = kick, 38 = snare, 42 = closed hi-hat)

Important music generation requirements:
1. Create separate instruments, each with its own track and patterns
2. Each instrument needs a unique channel (0-15, except percussion which is always 9)
3. Each instrument needs a soundfont_name that matches its type
4. Generate actual note data with precise timing
5. Create musically coherent patterns that work together
6. Ensure melodies follow music theory for the chosen key"""

        # Create a user prompt that specifies the requested music
        user_prompt = f"""Create a detailed music composition based on this description:

{description}

{f"Use a tempo of {tempo} BPM." if tempo else ""}

Each instrument should have appropriate notes, rhythms, and dynamics based on the description.
Be creative with instrument selection and musical patterns to match the requested style."""

        # Call the Claude API
        logger.debug("Calling Claude API with structured output prompt")
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
            logger.debug(f"Received response of length {len(response_text)} characters")
            
            # Try to parse the JSON directly
            try:
                # Parse the JSON
                music_description = json.loads(response_text)
                logger.debug("Successfully parsed JSON response")
                return music_description
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.debug(f"First 200 chars of response: {response_text[:200]}...")
                
                # Try to find JSON in the response as a fallback
                import re
                json_match = re.search(r'(\{[\s\S]*\})', response_text)
                
                if json_match:
                    try:
                        json_text = json_match.group(1)
                        logger.debug("Found JSON pattern, attempting to parse")
                        music_description = json.loads(json_text)
                        logger.debug("Successfully parsed JSON with fallback method")
                        return music_description
                    except json.JSONDecodeError as e2:
                        logger.error(f"Fallback parsing also failed: {e2}")
                        raise ValueError(f"Failed to parse JSON response: {e2}")
                else:
                    logger.error("No JSON-like structure found in response")
                    raise ValueError("No JSON found in Claude's response")
                
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            logger.debug(traceback.format_exc())
            raise