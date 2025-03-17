import os
import asyncio
import json
from app.services.midi import MIDIGenerator
from app.services.instruments import get_all_soundfonts, find_soundfonts

async def test_separate_midi_files():
    """Test the generation of separate MIDI files for each instrument."""
    
    # Create a test music description
    music_description = {
        "title": "Test Multi-Instrument Composition",
        "tempo": 120,
        "key": "C major",
        "time_signature": [4, 4],
        "instruments": [
            {
                "program": 0,  # Piano
                "name": "Piano",
                "soundfont_name": "Grand Piano",
                "channel": 0,
                "patterns": [
                    {
                        "type": "melody",
                        "notes": [
                            {"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80},
                            {"pitch": 64, "start": 1.0, "duration": 1.0, "velocity": 80},
                            {"pitch": 67, "start": 2.0, "duration": 1.0, "velocity": 80},
                            {"pitch": 72, "start": 3.0, "duration": 1.0, "velocity": 80},
                            {"pitch": 67, "start": 4.0, "duration": 1.0, "velocity": 80},
                            {"pitch": 64, "start": 5.0, "duration": 1.0, "velocity": 80},
                            {"pitch": 60, "start": 6.0, "duration": 2.0, "velocity": 80}
                        ]
                    }
                ]
            },
            {
                "program": 33,  # Electric Bass
                "name": "Bass",
                "soundfont_name": "Electric Bass Finger",
                "channel": 1,
                "patterns": [
                    {
                        "type": "bassline",
                        "notes": [
                            {"pitch": 36, "start": 0.0, "duration": 2.0, "velocity": 100},
                            {"pitch": 43, "start": 2.0, "duration": 2.0, "velocity": 100},
                            {"pitch": 38, "start": 4.0, "duration": 2.0, "velocity": 100},
                            {"pitch": 36, "start": 6.0, "duration": 2.0, "velocity": 100}
                        ]
                    }
                ]
            },
            {
                "program": "percussion",
                "name": "Drums",
                "soundfont_name": "Standard Drum Kit",
                "channel": 9,  # Channel 10 in MIDI (0-indexed in code)
                "patterns": [
                    {
                        "type": "rhythm",
                        "notes": [
                            # Kick drum (36)
                            {"pitch": 36, "start": 0.0, "duration": 0.1, "velocity": 100},
                            {"pitch": 36, "start": 2.0, "duration": 0.1, "velocity": 100},
                            {"pitch": 36, "start": 4.0, "duration": 0.1, "velocity": 100},
                            {"pitch": 36, "start": 6.0, "duration": 0.1, "velocity": 100},
                            
                            # Snare (38)
                            {"pitch": 38, "start": 1.0, "duration": 0.1, "velocity": 90},
                            {"pitch": 38, "start": 3.0, "duration": 0.1, "velocity": 90},
                            {"pitch": 38, "start": 5.0, "duration": 0.1, "velocity": 90},
                            {"pitch": 38, "start": 7.0, "duration": 0.1, "velocity": 90},
                            
                            # Hi-hat (42)
                            {"pitch": 42, "start": 0.0, "duration": 0.1, "velocity": 70},
                            {"pitch": 42, "start": 0.5, "duration": 0.1, "velocity": 70},
                            {"pitch": 42, "start": 1.0, "duration": 0.1, "velocity": 70},
                            {"pitch": 42, "start": 1.5, "duration": 0.1, "velocity": 70},
                            {"pitch": 42, "start": 2.0, "duration": 0.1, "velocity": 70},
                            {"pitch": 42, "start": 2.5, "duration": 0.1, "velocity": 70},
                            {"pitch": 42, "start": 3.0, "duration": 0.1, "velocity": 70},
                            {"pitch": 42, "start": 3.5, "duration": 0.1, "velocity": 70}
                        ]
                    }
                ]
            }
        ]
    }
    
    # Initialize the MIDI generator
    midi_generator = MIDIGenerator(output_dir="test_output")
    
    # Generate separate MIDI files
    results = await midi_generator.generate_midi_separate(music_description)
    
    # Print results
    print(f"Generated {len(results)} MIDI files:")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['instrument_name']} ({result['soundfont_name']}): {result['file_path']}")
    
    # Get the directory path
    dir_path = os.path.dirname(results[0]["file_path"]) if results else ""
    print(f"\nAll files are in: {dir_path}")
    
    # List all files in the directory
    if os.path.exists(dir_path):
        files = os.listdir(dir_path)
        print(f"\nFiles in directory ({len(files)}):")
        for file in files:
            file_path = os.path.join(dir_path, file)
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size} bytes)")
    
    return results

if __name__ == "__main__":
    # Run the test
    results = asyncio.run(test_separate_midi_files())
    
    # Print the first result in JSON format
    if results:
        print("\nFirst result structure:")
        result_dict = {
            "instrument_name": results[0]["instrument_name"],
            "soundfont_name": results[0]["soundfont_name"],
            "file_path": results[0]["file_path"],
            "track_count": results[0]["track_count"]
        }
        print(json.dumps(result_dict, indent=2))