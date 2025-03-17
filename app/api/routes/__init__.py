from fastapi import APIRouter
from app.api.routes.generate import router as generate_router
from app.api.routes.generate import (
    download_midi_file,
    get_composition,
    list_soundfonts
)

router = APIRouter()

# Include the generate router
router.include_router(generate_router, prefix="/generate", tags=["generation"])

# Re-export some endpoints directly at the API level for better URL structure
router.get("/download/{composition_dir}/{filename}", 
           tags=["files"])(download_midi_file)

router.get("/composition/{composition_dir_id}", 
           tags=["composition"])(get_composition)

router.get("/soundfonts", 
           tags=["soundfonts"])(list_soundfonts)