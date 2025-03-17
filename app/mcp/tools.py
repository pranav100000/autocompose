from typing import List, Dict, Any, Optional
import os
import logging
import json
import base64

from mcp.server.fastmcp import Context
from app.mcp.server import mcp
from app.services.instruments import (
    get_all_soundfonts,
    get_available_instrument_types,
    get_soundfonts_by_type,
    find_soundfonts,
    get_instrument_metadata,
    GM_INSTRUMENTS,
    GM_FAMILIES
)
from app.services.midi import MIDIGenerator

logger = logging.getLogger(__name__)

# Initialize MIDI generator
midi_generator = MIDIGenerator(output_dir="output")

@mcp.tool()
async def create_music_description(description: str, tempo: Optional[int] = None, key: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a detailed, structured music description from a text prompt.
    This tool generates a complete and valid JSON description of a musical piece based on your text description.
    
    The output will include:
    - Title for the composition
    - Appropriate tempo (or use the specified tempo)
    - Key signature
    - Time signature
    - Detailed instrument specifications with:
      - MIDI program numbers
      - Instrument names
      - Corresponding soundfont names
      - Channel assignments
      - Note patterns with precise timing, pitch, duration, and velocity
    
    IMPORTANT GUIDELINES:
    
    MIDI Technical Info:
    - MIDI pitches: Middle C = 60, C4 = 60, C5 = 72, etc. (12 semitones per octave)
    - Timing: measured in beats (e.g., 0.0, 1.0, 2.5)
    - Durations: in beats (e.g., 0.5 = eighth note in 4/4, 1.0 = quarter note)
    - Velocities: 1-127, with 64-100 being typical (127 = loudest)
    
    General MIDI Program Numbers:
    - Piano: 0-7 (0 = Acoustic Grand)
    - Bass: 32-39 (33 = Electric Bass)
    - Guitar: 24-31 (24 = Nylon, 25 = Steel, 30 = Distortion)
    - Strings: 40-47 (48-51 for ensembles)
    - Brass: 56-63
    - Percussion: Use channel 9 with program = "percussion"
      - Percussion notes: 36 = kick, 38 = snare, 42 = closed hi-hat
    
    Composition Tips:
    1. Each instrument should work both independently and together with others
    2. Each instrument needs its own channel (0-15, except percussion which is always 9)
    3. Each instrument needs a soundfont_name appropriate to its type
    4. Create musically coherent patterns that follow proper music theory for the key
    
    Common Soundfont Names:
    - "Grand Piano", "Electric Piano", "Acoustic Guitar", "Electric Guitar"
    - "Electric Bass (finger)", "Electric Bass (pick)", "Acoustic Bass"
    - "Violin", "Viola", "Cello", "String Ensemble"
    - "Trumpet", "Trombone", "Saxophone", "Brass Ensemble"
    - "Flute", "Clarinet", "Oboe"
    - "Synth Lead", "Synth Pad", "Synth Bass"
    - "Standard Drum Kit", "Jazz Drum Kit", "Rock Drum Kit"
    
    Args:
        description: Text description of the desired music
        tempo: Optional specific tempo in BPM
        key: Optional specific musical key
        
    Returns:
        Complete music description as a structured JSON object
    """
    # Get available instrument info to help with soundfont selection
    metadata = get_instrument_metadata()
    soundfonts = get_all_soundfonts()[:20]  # Limit to 20 examples to save context
    
    # Add the tempo if specified
    constraints = []
    if tempo:
        constraints.append(f"Tempo: {tempo} BPM")
    if key:
        constraints.append(f"Key: {key}")
        
    # Build a more detailed description
    full_description = description
    if constraints:
        full_description += "\n\nSpecific requirements:\n" + "\n".join(constraints)
    
    # Here we'd normally call the LLM directly, but since we're using MCP,
    # the MCP system will handle the LLM interaction for us.
    # This function just needs to return the structure that MCP will fill.
    
    # Define the expected structure that will be populated by the MCP system
    # This serves as a template - the actual values will come from the model
    return {
        "title": "",  # Will be filled by MCP
        "tempo": tempo or 120,  # Default to 120 if not specified
        "key": key or "",  # Will be filled by MCP if not specified
        "time_signature": [4, 4],  # Default time signature
        "instruments": []  # Will be filled by MCP
    }

@mcp.tool()
async def get_available_soundfonts(ctx: Context) -> Dict[str, Any]:
    """
    Get metadata about all available soundfonts.
    
    Returns:
        Dictionary containing soundfont metadata including types and counts
    """
    # Get metadata from the instrument service
    metadata = get_instrument_metadata()
    
    # Add a sample of available soundfonts (limiting to avoid overloading context)
    soundfonts = get_all_soundfonts()
    metadata["sample_soundfonts"] = soundfonts[:20] if len(soundfonts) > 20 else soundfonts
    
    return metadata

@mcp.tool()
async def search_soundfonts(query: str) -> List[Dict[str, Any]]:
    """
    Search for soundfonts matching a query.
    
    Args:
        query: Search string to match against soundfont names or types
        
    Returns:
        List of matching soundfont dictionaries
    """
    return find_soundfonts(query)

@mcp.tool()
async def get_soundfonts_by_instrument_type(instrument_type: str) -> List[Dict[str, Any]]:
    """
    Get soundfonts for a specific instrument type.
    
    Args:
        instrument_type: Type of instrument (e.g., "piano", "guitar", "strings")
        
    Returns:
        List of soundfonts of the specified type
    """
    return get_soundfonts_by_type(instrument_type)

@mcp.tool()
async def get_general_midi_instruments() -> Dict[str, Any]:
    """
    Get the General MIDI instrument program mappings.
    
    Returns:
        Dictionary containing GM program numbers, names, and families
    """
    return {
        "instruments": GM_INSTRUMENTS,
        "families": {k: list(v) for k, v in GM_FAMILIES.items()}
    }

@mcp.tool()
async def generate_midi_from_description(
    music_description: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate separate MIDI files for each instrument in a music description.
    
    The music description should be a JSON object with a detailed specification of the
    music to generate, including instruments, patterns, structure, etc. You have complete
    creative freedom to design the music as you see fit.
    
    For each instrument, ensure you include a "soundfont_name" field that specifies the
    soundfont that should be used to play that particular instrument's MIDI file.
    
    Example structure (you can modify as needed):
    {
        "title": "Song Title",
        "tempo": 120,
        "key": "C major",
        "time_signature": [4, 4],
        "instruments": [
            {
                "program": 0,  # GM program number
                "name": "Piano",
                "soundfont_name": "Grand Piano",  # For filename and playback
                "channel": 0,
                "patterns": [
                    {
                        "type": "melody",
                        "notes": [
                            {"pitch": 60, "start": 0, "duration": 1, "velocity": 80},
                            {"pitch": 62, "start": 1, "duration": 1, "velocity": 80},
                            ...
                        ]
                    }
                ]
            },
            ...
        ]
    }
    
    Args:
        music_description: Complete description of the music to generate
        
    Returns:
        Dictionary with generated MIDI data and metadata for each instrument
    """
    # Validate the music description
    required_fields = ["title", "tempo", "instruments"]
    for field in required_fields:
        if field not in music_description:
            raise ValueError(f"Missing required field in music description: {field}")
    
    # Check that each instrument has a soundfont_name
    for i, instrument in enumerate(music_description.get("instruments", [])):
        if "soundfont_name" not in instrument:
            # Default to instrument name if not specified
            instrument["soundfont_name"] = instrument.get("name", f"Instrument_{i}")
    
    # Generate separate MIDI files using the MIDI generator service
    results = await midi_generator.generate_midi_separate(music_description)
    
    # Get the directory path from the first result
    dir_path = os.path.dirname(results[0]["file_path"]) if results else ""
    
    # Create a structured response with all track information
    tracks = []
    composition_dir = os.path.basename(dir_path)
    for result in results:
        tracks.append({
            "instrument_name": result["instrument_name"],
            "soundfont_name": result["soundfont_name"],
            "file_path": result["file_path"],
            "track_count": result["track_count"],
            "midi_data": result["midi_data"],
            "download_url": f"/download/{composition_dir}/{os.path.basename(result['file_path'])}"
        })
    
    return {
        "title": music_description["title"],
        "directory": dir_path,
        "tracks": tracks
    }