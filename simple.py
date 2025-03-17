#!/usr/bin/env python
"""
A simplified server to test basic MIDI generation functionality.
"""
import os
import base64
import uuid
import mido
from mido import Message, MidiFile, MidiTrack
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

# Create output directory for MIDI files
os.makedirs("output", exist_ok=True)

app = FastAPI(
    title="AutoCompose Simple Server",
    description="Simple API for MIDI generation",
)

class MidiRequest(BaseModel):
    description: str
    tempo: Optional[int] = 120
    key: Optional[str] = "C Major"

class MidiResponse(BaseModel):
    title: str
    file_path: str
    download_url: str
    instruments: List[str]

@app.get("/")
def read_root():
    return {"message": "Welcome to AutoCompose Simple Server"}

@app.post("/generate")
def generate_midi(request: MidiRequest):
    """Generate a simple MIDI file based on the request."""
    # Create a MIDI file
    mid = MidiFile()
    
    # Add a track
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    tempo = mido.bpm2tempo(request.tempo)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    
    # Add track name
    track.append(mido.MetaMessage('track_name', name="Piano", time=0))
    
    # Set program (piano)
    track.append(Message('program_change', program=0, channel=0, time=0))
    
    # Add a simple C major scale
    for i, note in enumerate([60, 62, 64, 65, 67, 69, 71, 72]):
        # Note on
        track.append(Message('note_on', note=note, velocity=64, channel=0, time=0 if i > 0 else 0))
        # Note off
        track.append(Message('note_off', note=note, velocity=0, channel=0, time=480))
    
    # Generate unique file name
    file_name = f"midi_{uuid.uuid4().hex[:8]}.mid"
    file_path = os.path.join("output", file_name)
    
    # Save the file
    mid.save(file_path)
    
    return {
        "title": f"Music based on: {request.description[:30]}",
        "file_path": file_path,
        "download_url": f"/download/{file_name}",
        "instruments": ["Piano"]
    }

@app.get("/download/{filename}")
def download_midi(filename: str):
    """Download a generated MIDI file."""
    file_path = os.path.join("output", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/midi"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)