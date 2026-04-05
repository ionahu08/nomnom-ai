from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.food_log import FoodAnalysisResponse, FoodLogCreate, FoodLogResponse
from src.services.ai_service import analyze_food_photo as ai_analyze
from src.services.food_log_service import create_food_log, delete_food_log, list_today_logs
from src.services.photo_service import save_photo
from src.services.profile_service import get_profile

router = APIRouter(prefix="/api/v1/food-logs", tags=["food-logs"])


@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food_photo(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a food photo and get AI analysis. Does NOT save to database yet."""
    image_bytes = await file.read()

    # Save photo to disk
    photo_filename = save_photo(image_bytes, file.filename or "photo.jpg")

    # Get user's cat style preference
    profile = await get_profile(db, current_user.id)
    cat_style = profile.cat_style if profile else "sassy"

    # Call Haiku vision AI
    analysis = await ai_analyze(image_bytes, cat_style)
    return analysis


@router.post("/", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def save_food_log(
    data: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a confirmed food log after user reviews the AI analysis."""
    food_log = await create_food_log(db, current_user.id, data)
    return food_log


@router.get("/today", response_model=list[FoodLogResponse])
async def get_today_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all food logs for today."""
    logs = await list_today_logs(db, current_user.id)
    return logs


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_food_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a food log."""
    deleted = await delete_food_log(db, current_user.id, log_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found",
        )
