from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import ACTIVITY_MULTIPLIERS, CALORIES_PER_GRAM, DEFAULT_MACRO_SPLIT
from src.models.user import UserProfile
from src.schemas.user import MacroTargets, ProfileCreate, ProfileUpdate


def calculate_tdee(age: int, gender: str, height_cm: float, weight_kg: float, activity_level: str) -> int:
    """Calculate Total Daily Energy Expenditure using Mifflin-St Jeor equation."""
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier)


def calculate_macro_targets(tdee: int) -> MacroTargets:
    """Split TDEE into protein, carbs, and fat gram targets."""
    protein_cals = tdee * DEFAULT_MACRO_SPLIT["protein"]
    carb_cals = tdee * DEFAULT_MACRO_SPLIT["carbs"]
    fat_cals = tdee * DEFAULT_MACRO_SPLIT["fat"]

    return MacroTargets(
        calorie_target=tdee,
        protein_target=round(protein_cals / CALORIES_PER_GRAM["protein"]),
        carb_target=round(carb_cals / CALORIES_PER_GRAM["carbs"]),
        fat_target=round(fat_cals / CALORIES_PER_GRAM["fat"]),
    )


def get_effective_targets(profile: UserProfile) -> MacroTargets:
    """Get macro targets: use user overrides if set, otherwise calculate from TDEE."""
    tdee = calculate_tdee(
        profile.age, profile.gender, profile.height_cm, profile.weight_kg, profile.activity_level
    )
    calculated = calculate_macro_targets(tdee)

    return MacroTargets(
        calorie_target=profile.calorie_target or calculated.calorie_target,
        protein_target=profile.protein_target or calculated.protein_target,
        carb_target=profile.carb_target or calculated.carb_target,
        fat_target=profile.fat_target or calculated.fat_target,
    )


async def create_profile(db: AsyncSession, user_id: int, data: ProfileCreate) -> UserProfile:
    profile = UserProfile(user_id=user_id, **data.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_profile(db: AsyncSession, user_id: int) -> UserProfile | None:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def update_profile(db: AsyncSession, user_id: int, data: ProfileUpdate) -> UserProfile | None:
    profile = await get_profile(db, user_id)
    if profile is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile
