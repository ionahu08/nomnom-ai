from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NutrientSummary(BaseModel):
    """Summary of a single nutrient."""

    total: float
    average: float
    target: Optional[float] = None
    percentage: Optional[float] = None


class DailyBreakdown(BaseModel):
    """Daily nutrition breakdown."""

    date: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float


class TopFood(BaseModel):
    """Top food by frequency."""

    food: str
    count: int
    calories: int


class AnalyticsSummaryResponse(BaseModel):
    """Analytics summary for a period."""

    period: str  # "week" or "month"
    start_date: str
    end_date: str
    days_logged: int
    total_days: int
    consistency: float  # percentage of days logged

    calories: NutrientSummary
    protein_g: NutrientSummary
    carbs_g: NutrientSummary
    fat_g: NutrientSummary

    daily_breakdown: list[DailyBreakdown]
    top_foods: list[TopFood]

    class Config:
        json_schema_extra = {
            "example": {
                "period": "week",
                "start_date": "2026-06-09",
                "end_date": "2026-06-15",
                "days_logged": 6,
                "total_days": 7,
                "consistency": 85.7,
                "calories": {"total": 12950, "average": 1850, "target": 2000, "percentage": 92.5},
                "protein_g": {"total": 840, "average": 120, "target": 150, "percentage": 80},
                "carbs_g": {"total": 1260, "average": 180, "target": 200, "percentage": 90},
                "fat_g": {"total": 420, "average": 60, "target": 65, "percentage": 92},
                "daily_breakdown": [
                    {
                        "date": "2026-06-09",
                        "calories": 1950,
                        "protein_g": 125,
                        "carbs_g": 185,
                        "fat_g": 62,
                    }
                ],
                "top_foods": [
                    {"food": "Noodles", "count": 5, "calories": 1200},
                    {"food": "Chicken Breast", "count": 4, "calories": 800},
                ],
            }
        }
