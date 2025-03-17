from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional, Any
import os
import logging
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP, Context

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Create a context class for dependency injection
@dataclass
class AppContext:
    soundfont_dir: str


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Set up application resources on startup and clean up on shutdown."""
    # Initialize soundfont directory
    soundfont_dir = os.path.join(os.getcwd(), "soundfonts")
    
    # Could add more initialization here (database, etc.)
    
    try:
        yield AppContext(soundfont_dir=soundfont_dir)
    finally:
        # Any cleanup code would go here
        pass


# Create the MCP server - let it get settings from environment variables
# Environment variables are set in .env file (MCP_LOG_LEVEL, MCP_HOST, MCP_PORT)
mcp = FastMCP(
    "AutoCompose", 
    lifespan=app_lifespan
)