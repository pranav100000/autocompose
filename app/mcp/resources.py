from app.mcp.server import mcp

# Core resource for system capabilities
@mcp.resource("autocompose://capabilities")
def get_capabilities() -> str:
    """
    Provides information about AutoCompose capabilities.
    """
    return """
    AutoCompose: Text-to-MIDI Generation System
    
    Core capabilities:
    - Generate MIDI music from text descriptions
    - Select appropriate instruments from soundfont library
    - Create melodies, harmonies, and rhythms
    - Support for all General MIDI instrument programs
    
    Usage workflow:
    1. Browse available soundfonts using the tools
    2. Design a musical composition matching the text description
    3. Create the MIDI file with precise note-level control
    
    The system is designed to give you (the LLM) complete creative freedom.
    You're encouraged to use your musical knowledge to create compositions
    that match the user's description.
    """

# Resource for interacting with the system
@mcp.resource("autocompose://workflow")
def get_workflow() -> str:
    """
    Provides information about the AutoCompose workflow.
    """
    return """
    AutoCompose Workflow:
    
    1. EXPLORE soundfonts
       - Use get_available_soundfonts to see what's available
       - Use search_soundfonts to find specific instruments
       - Use get_soundfonts_by_instrument_type for instrument categories
    
    2. DESIGN the composition
       - Select appropriate instruments based on the description
       - Design musical patterns (melodies, chords, rhythms)
       - Structure the composition (intro, verse, chorus, etc.)
    
    3. CREATE the music description object
       - A complete JSON object with all musical details
       - Include title, tempo, key, time signature
       - Define instruments with GM program numbers
       - Specify note patterns with exact pitch, timing, duration
    
    4. GENERATE the MIDI file
       - Use generate_midi_from_description with your music description
       - The result includes the MIDI data and download URL
    
    Remember: You have complete creative control over the musical content.
    Use your knowledge of music theory and composition to create high-quality music.
    """

# Resource for MIDI format reference
@mcp.resource("autocompose://midi_format")
def get_midi_format() -> str:
    """
    Provides information about the MIDI format used by AutoCompose.
    """
    return """
    AutoCompose MIDI Format Reference:
    
    The music description should be a JSON object with this structure:
    
    {
      "title": "Song Title",
      "tempo": 120,                    // BPM
      "key": "C major",                // Musical key
      "time_signature": [4, 4],        // [numerator, denominator]
      "instruments": [
        {
          "program": 0,                // GM program number (0-127)
          "name": "Piano",             // Display name
          "channel": 0,                // MIDI channel (0-15, 9=percussion)
          "patterns": [
            {
              "type": "melody",        // Pattern type (melody, chords, etc.)
              "notes": [
                {
                  "pitch": 60,         // MIDI note number (0-127, 60=middle C)
                  "start": 0.0,        // Start time in beats (0.0 = beginning)
                  "duration": 1.0,     // Duration in beats
                  "velocity": 80       // Note velocity (0-127)
                },
                // More notes...
              ]
            }
            // More patterns...
          ]
        }
        // More instruments...
      ]
    }
    
    Important notes:
    - For percussion (GM program = percussion), use channel 9 (MIDI channel 10)
    - Percussion notes use specific pitch values (see GM percussion map)
    - Pitches: Middle C = 60, C3 = 48, C4 = 60, C5 = 72
    - Common velocity values: ff=100-127, mf=64-80, pp=1-20
    """