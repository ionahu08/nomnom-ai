from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.database import get_db
from src.llm.cache import SemanticCache
from src.models.user import User
from src.schemas.food_log import (
    DayCalendarSummary,
    FoodAnalysisResponse,
    FoodLogCreate,
    FoodLogResponse,
    FoodLogUpdate,
)
from src.services.ai_service import analyze_food_photo as ai_analyze
from src.services.food_log_service import (
    create_food_log,
    delete_food_log,
    list_calendar_summary,
    list_logs_for_date,
    list_today_logs,
)
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

    # Call Haiku vision AI (with semantic cache check)
    analysis = await ai_analyze(image_bytes, cat_style, db=db)

    # Add photo path to the response
    return analysis.model_copy(update={"photo_path": photo_filename})


@router.post("/", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def save_food_log(
    data: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a confirmed food log after user reviews the AI analysis."""
    food_log = await create_food_log(db, current_user.id, data)

    # Cache the analysis for semantic search (for future similar meals)
    await SemanticCache.cache_analysis(
        db=db,
        food_description=data.food_name,
        food_log_id=food_log.id,
    )

    return food_log


@router.get("/today", response_model=list[FoodLogResponse])
async def get_today_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all food logs for today."""
    logs = await list_today_logs(db, current_user.id)
    return logs


@router.get("/by-date", response_model=list[FoodLogResponse])
async def get_logs_by_date(
    date: str,  # "YYYY-MM-DD"
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all food logs for a specific date."""
    try:
        target_date = date_type.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")

    logs = await list_logs_for_date(db, current_user.id, target_date)
    return logs


@router.get("/calendar-summary", response_model=list[DayCalendarSummary])
async def get_calendar_summary(
    start: str,  # "YYYY-MM-DD"
    end: str,  # "YYYY-MM-DD"
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch calendar summary (per-day metadata) for a date range."""
    try:
        start_date = date_type.fromisoformat(start)
        end_date = date_type.fromisoformat(end)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")

    summary = await list_calendar_summary(db, current_user.id, start_date, end_date)
    return summary


@router.patch("/{log_id}", response_model=FoodLogResponse)
async def update_food_log(
    log_id: int,
    data: FoodLogUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a food log (mark as user corrected)."""
    from sqlalchemy import select
    from src.models.food_log import FoodLog

    # Get the food log
    stmt = select(FoodLog).where(FoodLog.id == log_id).where(FoodLog.user_id == current_user.id)
    result = await db.execute(stmt)
    food_log = result.scalar_one_or_none()

    if not food_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found",
        )

    # Update food name and mark as corrected
    food_log.food_name = data.food_name
    food_log.is_user_corrected = True

    # Update meal type if provided
    if data.meal_type is not None:
        food_log.meal_type = data.meal_type

    await db.commit()
    await db.refresh(food_log)

    return food_log


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
