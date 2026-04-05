import os
import uuid
from pathlib import Path

from src.config import settings


def save_photo(image_bytes: bytes, filename: str) -> str:
    """Save uploaded photo to disk and return the relative path."""
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)

    # Generate unique filename to avoid collisions
    ext = Path(filename).suffix or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return unique_name


def get_photo_path(filename: str) -> Path | None:
    """Get full path to a photo file, or None if it doesn't exist."""
    path = Path(settings.upload_dir) / filename
    if path.exists():
        return path
    return None


def delete_photo(filename: str) -> bool:
    """Delete a photo file. Returns True if deleted, False if not found."""
    path = Path(settings.upload_dir) / filename
    if path.exists():
        os.remove(path)
        return True
    return False
