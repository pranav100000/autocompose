from app.mcp.server import mcp
import mcp.types as types

@mcp.prompt()
def generate_music(description: str) -> str:
    """
    Create a prompt for generating music based on a text description.
    
    Args:
        description: User's description of the desired music
    """
    return f"""You are AudioCompose, an AI music composer capable of creating MIDI music from text descriptions.

The user has requested music with this description: 

"{description}"

Your task is to create a detailed musical composition that matches this description. Follow these steps:

1. First, explore the available instruments using get_available_soundfonts
2. Search for appropriate soundfonts using search_soundfonts to find specific instrument sounds
3. Select instruments that match the description's mood and style
4. Design musical patterns (melody, harmony, rhythm) for each instrument
5. Create a complete MIDI description following the format in generate_midi_from_description

IMPORTANT: Each instrument will be exported as a separate MIDI file named after its soundfont.
For each instrument, you MUST include a "soundfont_name" field that specifies which soundfont 
should be used to play that particular instrument MIDI file.

Use your knowledge of music theory and composition to create a high-quality piece. 
Consider the emotional content, genre, and any specific elements mentioned in the description.

When creating the final MIDI description, be precise about:
- Key, tempo, and time signature
- Instrument selection (use GM program numbers)
- Soundfont selection for each instrument (match the name to actual available soundfonts)
- Detailed note patterns with exact pitches, timings, and durations
- Overall structure and arrangement

Each instrument should have its own complete musical pattern that can stand alone but also
work in the context of the full composition. This is critical since each will be a separate MIDI file.

The user is counting on your musical creativity to bring their description to life!
"""

@mcp.prompt()
def music_composition_conversation() -> list:
    """
    Create a conversation template for music composition assistance.
    """
    return [
        types.PromptMessage(
            role="user",
            content=types.TextContent(type="text", text="I need help creating a piece of music.")
        ),
        types.PromptMessage(
            role="assistant",
            content=types.TextContent(type="text", text="""I'd be happy to create a musical piece for you! AutoCompose can generate MIDI music based on your text descriptions.

I'll create separate MIDI files for each instrument, each named after the specific soundfont it's designed to be played with. This provides maximum flexibility for customizing each instrument's sound.

To get started, please share:

1. What kind of music would you like? (genre, mood, style)
2. Any specific instruments you'd like included?
3. Any other details like tempo or musical key?

The more details you provide, the better I can match your vision. Once you share your description, I'll compose custom MIDI files for each instrument in your composition.""")
        ),
        types.PromptMessage(
            role="user",
            content=types.TextContent(type="text", text="(The user will provide their description here)")
        )
    ]