from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

# Create output directory for MIDI files
os.makedirs("output", exist_ok=True)

app = FastAPI(
    title="AutoCompose",
    description="API for generating MIDI music from text descriptions",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to AutoCompose API"}

# Legacy download endpoint - now handled by /api/download/{composition_dir}/{filename}
# However, we'll keep this for backward compatibility
@app.get("/download/{filename}")
async def download_midi(filename: str):
    """
    Download a generated MIDI file by filename (legacy endpoint).
    For newer MIDI files, use /api/download/{composition_dir}/{filename}
    """
    # Try direct path first
    file_path = os.path.join("output", filename)
    
    # If not found, search in subdirectories
    if not os.path.exists(file_path):
        for root, _, files in os.walk("output"):
            for file in files:
                if file == filename:
                    file_path = os.path.join(root, file)
                    break
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="MIDI file not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/midi"
    )

# Import and include routers
from app.api.routes import router as api_router
app.include_router(api_router, prefix="/api")