#!/usr/bin/env python3
"""
Create a test MIDI file to verify the MIDI generator implementation.
"""
import os
import mido
from mido import Message, MidiFile, MidiTrack

def create_test_midi():
    """Create a simple test MIDI file."""
    # Create output directory if needed
    os.makedirs("output", exist_ok=True)
    
    # Create a new MIDI file with timing information
    midi_file = MidiFile()
    
    # Create piano track
    piano_track = MidiTrack()
    midi_file.tracks.append(piano_track)
    
    # Set tempo
    tempo = mido.bpm2tempo(120)
    piano_track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    
    # Add track name
    piano_track.append(mido.MetaMessage('track_name', name="Piano", time=0))
    
    # Set program (piano)
    piano_track.append(Message('program_change', program=0, channel=0, time=0))
    
    # Add notes (C major scale)
    notes = [60, 62, 64, 65, 67, 69, 71, 72]
    
    for i, note in enumerate(notes):
        # Note on
        piano_track.append(Message('note_on', note=note, velocity=64, channel=0, time=0 if i > 0 else 0))
        # Note off (after 1 beat)
        piano_track.append(Message('note_off', note=note, velocity=0, channel=0, time=480))
    
    # Add drums
    drum_track = MidiTrack()
    midi_file.tracks.append(drum_track)
    
    # Add track name
    drum_track.append(mido.MetaMessage('track_name', name="Drums", time=0))
    
    # Drum notes (hi-hat, kick, snare pattern)
    for i in range(8):
        # Hi-hat
        drum_track.append(Message('note_on', note=42, velocity=64, channel=9, time=0 if i > 0 else 0))
        drum_track.append(Message('note_off', note=42, velocity=0, channel=9, time=120))
        
        # Kick on beats 1 and 3
        if i % 2 == 0:
            drum_track.append(Message('note_on', note=36, velocity=100, channel=9, time=0))
            drum_track.append(Message('note_off', note=36, velocity=0, channel=9, time=120))
        
        # Snare on beats 2 and 4
        if i % 2 == 1:
            drum_track.append(Message('note_on', note=38, velocity=100, channel=9, time=0))
            drum_track.append(Message('note_off', note=38, velocity=0, channel=9, time=120))
    
    # Save the MIDI file
    output_path = "output/test_midi.mid"
    midi_file.save(output_path)
    print(f"Created test MIDI file: {output_path}")

if __name__ == "__main__":
    create_test_midi()