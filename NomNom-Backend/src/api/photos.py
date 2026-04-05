from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from src.services.photo_service import get_photo_path

router = APIRouter(prefix="/api/v1/photos", tags=["photos"])


@router.get("/{filename}")
async def serve_photo(filename: str):
    """Serve an uploaded food photo."""
    path = get_photo_path(filename)
    if path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    return FileResponse(path)
