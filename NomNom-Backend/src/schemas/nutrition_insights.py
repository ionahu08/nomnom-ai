from pydantic import BaseModel, Field
from typing import Optional


class NutrientData(BaseModel):
    total: float
    target: int
    percentage: float


class PeriodData(BaseModel):
    start_date: str
    end_date: str
    calories: NutrientData
    protein: NutrientData
    carbs: NutrientData
    fat: NutrientData
    foods: list[str] = Field(default_factory=list)


class HealthProfile(BaseModel):
    age: Optional[int] = None
    goal: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    allergies: Optional[list[str]] = None
    medical_conditions: Optional[list[str]] = None
    calorie_target: int
    protein_target: int
    carb_target: int
    fat_target: int


class NutritionGap(BaseModel):
    nutrient: str
    foods: list[str]
    reasoning: str


class NutritionAnalysis(BaseModel):
    summary: str
    strengths: list[str]
    gaps: list[str]
    recommendations: list[NutritionGap]


class NutritionInsightsResponse(BaseModel):
    periods: dict[str, PeriodData]
    health_profile: HealthProfile
    analysis: Optional[NutritionAnalysis] = None
