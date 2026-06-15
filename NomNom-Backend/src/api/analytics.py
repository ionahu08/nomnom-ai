from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database import get_db
from src.models.user import User
from src.repositories.analytics_repository import AnalyticsRepository
from src.schemas.analytics import AnalyticsSummaryResponse, NutrientSummary

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    period: Annotated[Literal["week", "month"], Query(description="Time period")],
    date: Annotated[str, Query(description="End date (YYYY-MM-DD), default: today")] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalyticsSummaryResponse:
    """
    Get nutrition analytics summary for a week or month.

    Query parameters:
    - period: "week" or "month"
    - date: End date in YYYY-MM-DD format (optional, defaults to today)
    """
    # Parse end date
    if date:
        try:
            end_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        end_date = datetime.now(timezone.utc)

    # Calculate start date based on period
    if period == "week":
        start_date = end_date - timedelta(days=7)
        total_days = 7
    elif period == "month":
        start_date = end_date - timedelta(days=30)
        total_days = 30
    else:
        raise HTTPException(status_code=400, detail="Period must be 'week' or 'month'")

    # Fetch aggregated stats
    stats = await AnalyticsRepository.get_aggregated_stats(db, current_user.id, start_date, end_date)

    # Get user targets
    targets = await AnalyticsRepository.get_user_targets(db, current_user.id)

    # Get days logged
    days_logged, _ = await AnalyticsRepository.get_days_logged(db, current_user.id, start_date, end_date)

    # Calculate consistency percentage
    consistency = (days_logged / total_days * 100) if total_days > 0 else 0

    # Build nutrient summaries with targets and percentages
    calories_summary = NutrientSummary(
        total=stats["calories"]["total"],
        average=stats["calories"]["average"],
        target=targets["calorie_target"],
        percentage=round(
            (stats["calories"]["average"] / targets["calorie_target"] * 100), 1
        )
        if targets["calorie_target"]
        else None,
    )

    protein_summary = NutrientSummary(
        total=stats["protein_g"]["total"],
        average=stats["protein_g"]["average"],
        target=targets["protein_target"],
        percentage=round(
            (stats["protein_g"]["average"] / targets["protein_target"] * 100), 1
        )
        if targets["protein_target"]
        else None,
    )

    carbs_summary = NutrientSummary(
        total=stats["carbs_g"]["total"],
        average=stats["carbs_g"]["average"],
        target=targets["carb_target"],
        percentage=round((stats["carbs_g"]["average"] / targets["carb_target"] * 100), 1)
        if targets["carb_target"]
        else None,
    )

    fat_summary = NutrientSummary(
        total=stats["fat_g"]["total"],
        average=stats["fat_g"]["average"],
        target=targets["fat_target"],
        percentage=round((stats["fat_g"]["average"] / targets["fat_target"] * 100), 1)
        if targets["fat_target"]
        else None,
    )

    return AnalyticsSummaryResponse(
        period=period,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        days_logged=days_logged,
        total_days=total_days,
        consistency=round(consistency, 1),
        calories=calories_summary,
        protein_g=protein_summary,
        carbs_g=carbs_summary,
        fat_g=fat_summary,
        daily_breakdown=stats["daily_breakdown"],
        top_foods=stats["top_foods"],
    )
