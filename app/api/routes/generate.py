from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import base64
import os
import json
import logging

from app.services.llm import generate_music_instructions, run_mcp_session
from app.services.midi import MIDIGenerator
from app.services.instruments import get_all_soundfonts, find_soundfonts

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

class MusicGenerationRequest(BaseModel):
    """Request for generating music from a text description."""
    description: str
    key: Optional[str] = None
    tempo: Optional[int] = None
    duration: Optional[int] = None
    genre: Optional[str] = None

class MidiTrackData(BaseModel):
    """Data for a single MIDI track/instrument."""
    instrument_name: str
    soundfont_name: str
    file_path: str
    midi_data: str  # Base64 encoded MIDI data
    download_url: str
    track_count: int

class MusicGenerationResponse(BaseModel):
    """Response containing generated MIDI music."""
    title: str
    directory: str  # Path to the directory containing all MIDI files
    tracks: List[MidiTrackData]  # Individual instrument tracks

class SoundfontListResponse(BaseModel):
    """Response containing a list of available soundfonts."""
    total: int
    soundfonts: List[Dict[str, Any]]

# Initialize MIDI generator
midi_generator = MIDIGenerator(output_dir="output")

@router.post("/music", response_model=MusicGenerationResponse)
async def generate_music(request: MusicGenerationRequest):
    """
    Generate MIDI music based on a text description.
    
    Uses the Model Context Protocol (MCP) to interpret the description
    and generate appropriate MIDI music. Generates separate MIDI files
    for each instrument, each meant to be played with a specific soundfont.
    """
    try:
        import sys
        import json
        import logging
        import asyncio
        from app.mcp.server import mcp

        # Prepare the full description with any constraints
        full_description = request.description
        constraints = []
        
        if request.key:
            constraints.append(f"Key: {request.key}")
        if request.tempo:
            constraints.append(f"Tempo: {request.tempo} BPM")
        if request.duration:
            constraints.append(f"Duration: approximately {request.duration} seconds")
        if request.genre:
            constraints.append(f"Genre: {request.genre}")
        
        if constraints:
            full_description += "\n\nAdditional constraints:\n" + "\n".join(constraints)
        
        logger.info(f"Starting music generation for: {full_description[:100]}...")
        
        # Run an MCP session to generate the music description
        # This will use the tools defined in app/mcp/tools.py
        mcp_result = await run_mcp_session(full_description)
        
        # We expect the result to contain a complete music description
        # This should come from the MCP generate_midi_from_description tool
        if "music_description" not in mcp_result:
            logger.error("MCP session failed to generate a music description")
            logger.debug(f"MCP result: {mcp_result}")
            raise ValueError("Failed to generate music description through MCP")
        
        # Extract the music description from the MCP result
        music_description = mcp_result["music_description"]
        
        # Log what was generated
        logger.info(f"Generated music description: {music_description['title']}")
        logger.info(f"Number of instruments: {len(music_description.get('instruments', []))}")
        for i, instrument in enumerate(music_description.get('instruments', [])):
            logger.info(f"Instrument {i+1}: {instrument.get('name')} ({instrument.get('soundfont_name')})")
        
        # Step 3: Generate separate MIDI files for each instrument
        results = await midi_generator.generate_midi_separate(music_description)
        
        # Get the directory path from the first result
        dir_path = os.path.dirname(results[0]["file_path"]) if results else ""
        
        # Step 4: Transform results into response model format
        tracks = []
        composition_dir = os.path.basename(dir_path)
        for result in results:
            tracks.append(MidiTrackData(
                instrument_name=result["instrument_name"],
                soundfont_name=result["soundfont_name"],
                file_path=result["file_path"],
                midi_data=result["midi_data"],
                download_url=f"/download/{composition_dir}/{os.path.basename(result['file_path'])}",
                track_count=result["track_count"]
            ))
        
        # Step 5: Return the response
        return MusicGenerationResponse(
            title=music_description["title"],
            directory=dir_path,
            tracks=tracks
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating music: {str(e)}"
        )

@router.get("/download/{composition_dir}/{filename}", name="download_midi_file")
async def download_midi_file(composition_dir: str, filename: str):
    """
    Download a specific MIDI file from a composition.
    
    Args:
        composition_dir: Directory name of the composition (URL-encoded)
        filename: Name of the MIDI file to download (URL-encoded)
    """
    try:
        # URL-decode the parameters
        from urllib.parse import unquote
        composition_dir = unquote(composition_dir)
        filename = unquote(filename)
        
        file_path = os.path.join("output", composition_dir, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            # Try to find a similar file
            dir_path = os.path.join("output", composition_dir)
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.lower() == filename.lower() or filename in file:
                        file_path = os.path.join(dir_path, file)
                        filename = file
                        break
        
        # Check again if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"MIDI file not found: {filename}"
            )
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="audio/midi"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading MIDI file: {str(e)}"
        )

@router.get("/composition/{composition_dir_id}", name="get_composition")
async def get_composition(composition_dir_id: str):
    """
    Get all MIDI files for a specific composition.
    
    Args:
        composition_dir_id: Directory ID (can be the full name or an encoded ID)
    """
    try:
        # List all directories in the output folder
        output_dir = "output"
        if not os.path.exists(output_dir):
            raise HTTPException(
                status_code=404,
                detail="No compositions available"
            )
        
        # Try to find a matching directory
        matching_dirs = []
        for dir_name in os.listdir(output_dir):
            dir_path = os.path.join(output_dir, dir_name)
            if os.path.isdir(dir_path) and (composition_dir_id in dir_name or composition_dir_id == dir_name):
                matching_dirs.append(dir_path)
        
        if not matching_dirs:
            raise HTTPException(
                status_code=404,
                detail=f"Composition not found: {composition_dir_id}"
            )
        
        # Use the first matching directory
        dir_path = matching_dirs[0]
        composition_dir = os.path.basename(dir_path)
        
        # Get all MIDI files in the directory
        midi_files = []
        for file in os.listdir(dir_path):
            if file.lower().endswith(".mid"):
                file_path = os.path.join(dir_path, file)
                
                # Read file data for return
                with open(file_path, 'rb') as f:
                    midi_data = base64.b64encode(f.read()).decode('utf-8')
                
                # URL-encode the filename and composition dir for the download URL
                from urllib.parse import quote
                encoded_comp_dir = quote(composition_dir)
                encoded_filename = quote(file)
                
                midi_files.append({
                    "filename": file,
                    "file_path": file_path,
                    "soundfont_name": os.path.splitext(file)[0],
                    "midi_data": midi_data,
                    "download_url": f"/download/{encoded_comp_dir}/{encoded_filename}"
                })
        
        return {
            "composition_dir": composition_dir,
            "midi_files": midi_files,
            "file_count": len(midi_files)
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving composition: {str(e)}"
        )

@router.get("/soundfonts", response_model=SoundfontListResponse)
async def list_soundfonts(query: Optional[str] = None):
    """
    List available soundfont files.
    
    Args:
        query: Optional search string to filter soundfonts
    """
    try:
        if query:
            soundfonts = find_soundfonts(query)
        else:
            soundfonts = get_all_soundfonts()
        
        return SoundfontListResponse(
            total=len(soundfonts),
            soundfonts=soundfonts
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing soundfonts: {str(e)}"
        )