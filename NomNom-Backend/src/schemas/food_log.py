from datetime import datetime

from pydantic import BaseModel


class FoodAnalysisResponse(BaseModel):
    """What the AI returns after analyzing a food photo."""
    food_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    food_category: str | None = None
    cuisine_origin: str | None = None
    cat_roast: str


class FoodLogCreate(BaseModel):
    """Save a confirmed food log (after user reviews AI analysis)."""
    photo_path: str
    food_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    food_category: str | None = None
    cuisine_origin: str | None = None
    cat_roast: str
    ai_raw_response: dict | None = None


class FoodLogResponse(BaseModel):
    """A food log entry returned from the API."""
    id: int
    user_id: int
    photo_path: str
    food_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    food_category: str | None
    cuisine_origin: str | None
    cat_roast: str
    is_user_corrected: bool
    logged_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
