from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.user import ProfileCreate, ProfileResponse, ProfileUpdate
from src.services.profile_service import (
    create_profile,
    get_effective_targets,
    get_profile,
    update_profile,
)

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await get_profile(db, current_user.id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists",
        )
    profile = await create_profile(db, current_user.id, data)
    targets = get_effective_targets(profile)
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        age=profile.age,
        gender=profile.gender,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=profile.activity_level,
        cat_style=profile.cat_style,
        allergies=profile.allergies,
        dietary_restrictions=profile.dietary_restrictions,
        cuisine_preferences=profile.cuisine_preferences,
        calorie_target=profile.calorie_target,
        protein_target=profile.protein_target,
        carb_target=profile.carb_target,
        fat_target=profile.fat_target,
        notification_enabled=profile.notification_enabled,
        targets=targets,
    )


@router.get("/", response_model=ProfileResponse)
@router.get("", response_model=ProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(db, current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Complete onboarding first.",
        )
    targets = get_effective_targets(profile)
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        age=profile.age,
        gender=profile.gender,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=profile.activity_level,
        cat_style=profile.cat_style,
        allergies=profile.allergies,
        dietary_restrictions=profile.dietary_restrictions,
        cuisine_preferences=profile.cuisine_preferences,
        calorie_target=profile.calorie_target,
        protein_target=profile.protein_target,
        carb_target=profile.carb_target,
        fat_target=profile.fat_target,
        notification_enabled=profile.notification_enabled,
        targets=targets,
    )


@router.patch("/", response_model=ProfileResponse)
async def update_user_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await update_profile(db, current_user.id, data)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Complete onboarding first.",
        )
    targets = get_effective_targets(profile)
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        age=profile.age,
        gender=profile.gender,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=profile.activity_level,
        cat_style=profile.cat_style,
        allergies=profile.allergies,
        dietary_restrictions=profile.dietary_restrictions,
        cuisine_preferences=profile.cuisine_preferences,
        calorie_target=profile.calorie_target,
        protein_target=profile.protein_target,
        carb_target=profile.carb_target,
        fat_target=profile.fat_target,
        notification_enabled=profile.notification_enabled,
        targets=targets,
    )
