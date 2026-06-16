from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.database import get_db
from src.models.user import User
from src.repositories.analytics_repository import AnalyticsRepository
from src.schemas.nutrition_insights import (
    NutritionInsightsResponse,
    PeriodData,
    NutrientData,
    HealthProfile,
)

router = APIRouter(prefix="/api/v1/nutrition", tags=["nutrition"])


@router.get("/insights", response_model=NutritionInsightsResponse)
async def get_nutrition_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NutritionInsightsResponse:
    """
    Get personalized nutrition insights for past 1 day, 1 week, and 1 month.

    Returns:
    - Multi-period nutrition data (all three periods at once)
    - User's health profile (goals, targets, allergies, conditions)
    - AI analysis and recommendations (populated in Phase 2)
    """
    end_date = datetime.now(timezone.utc)

    # Fetch data for three periods
    periods = {}
    period_configs = {
        "day": 1,
        "week": 7,
        "month": 30,
    }

    for period_name, days in period_configs.items():
        start_date = end_date - timedelta(days=days)

        # Fetch aggregated stats
        stats = await AnalyticsRepository.get_aggregated_stats(
            db, current_user.id, start_date, end_date
        )

        # Fetch user targets
        targets = await AnalyticsRepository.get_user_targets(db, current_user.id)

        # Get days logged
        days_logged, total_days = await AnalyticsRepository.get_days_logged(
            db, current_user.id, start_date, end_date
        )

        # Fetch food logs to get food names
        food_logs = await AnalyticsRepository.get_food_logs_for_period(
            db, current_user.id, start_date, end_date
        )

        # Extract unique foods from logs
        foods = list(set(log.food_name for log in food_logs if log.food_name))[:20]  # Top 20 unique foods

        # Build period data
        periods[period_name] = PeriodData(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            calories=NutrientData(
                total=stats.get("calories", {}).get("total", 0),
                target=targets.get("calorie_target", 2000),
                percentage=(
                    (stats.get("calories", {}).get("total", 0) / targets.get("calorie_target", 2000) * 100)
                    if targets.get("calorie_target", 0) > 0
                    else 0
                ),
            ),
            protein=NutrientData(
                total=stats.get("protein", {}).get("total", 0),
                target=targets.get("protein_target", 150),
                percentage=(
                    (stats.get("protein", {}).get("total", 0) / targets.get("protein_target", 150) * 100)
                    if targets.get("protein_target", 0) > 0
                    else 0
                ),
            ),
            carbs=NutrientData(
                total=stats.get("carbs", {}).get("total", 0),
                target=targets.get("carb_target", 200),
                percentage=(
                    (stats.get("carbs", {}).get("total", 0) / targets.get("carb_target", 200) * 100)
                    if targets.get("carb_target", 0) > 0
                    else 0
                ),
            ),
            fat=NutrientData(
                total=stats.get("fat", {}).get("total", 0),
                target=targets.get("fat_target", 65),
                percentage=(
                    (stats.get("fat", {}).get("total", 0) / targets.get("fat_target", 65) * 100)
                    if targets.get("fat_target", 0) > 0
                    else 0
                ),
            ),
            foods=foods,
        )

    # Fetch user health profile
    user_profile = current_user.profile

    health_profile = HealthProfile(
        age=user_profile.age if user_profile else None,
        goal=user_profile.goal if user_profile else None,
        height_cm=int(user_profile.height_cm) if user_profile else None,
        weight_kg=user_profile.weight_kg if user_profile else None,
        allergies=user_profile.allergies if user_profile else None,
        medical_conditions=user_profile.medical_conditions if user_profile else None,
        calorie_target=int(
            user_profile.calorie_target if user_profile and user_profile.calorie_target else 2000
        ),
        protein_target=int(
            user_profile.protein_target if user_profile and user_profile.protein_target else 150
        ),
        carb_target=int(
            user_profile.carb_target if user_profile and user_profile.carb_target else 200
        ),
        fat_target=int(
            user_profile.fat_target if user_profile and user_profile.fat_target else 65
        ),
    )

    return NutritionInsightsResponse(
        periods=periods,
        health_profile=health_profile,
        analysis=None,  # Will be populated in Phase 2
    )
