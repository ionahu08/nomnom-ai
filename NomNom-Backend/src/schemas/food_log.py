from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FoodAnalysisResponse(BaseModel):
    """What the AI returns after analyzing a food photo."""
    food_name: str = Field(..., min_length=1, max_length=200, description="Name of the food")
    calories: int = Field(..., ge=0, le=5000, description="Estimated calories (0-5000)")
    protein_g: float = Field(..., ge=0, le=500, description="Protein in grams (0-500)")
    carbs_g: float = Field(..., ge=0, le=500, description="Carbs in grams (0-500)")
    fat_g: float = Field(..., ge=0, le=500, description="Fat in grams (0-500)")
    photo_path: str = ""
    food_category: str | None = Field(None, max_length=100, description="Food category")
    cuisine_origin: str | None = Field(None, max_length=100, description="Cuisine origin")
    cat_roast: str = Field(..., min_length=1, max_length=500, description="Funny roast")

    @field_validator("food_name")
    @classmethod
    def validate_food_name(cls, v: str) -> str:
        """Ensure food name is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Food name cannot be empty")
        return v.strip()

    @field_validator("cat_roast")
    @classmethod
    def validate_cat_roast(cls, v: str) -> str:
        """Ensure roast is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Cat roast cannot be empty")
        return v.strip()

    @field_validator("calories")
    @classmethod
    def validate_calories(cls, v: int) -> int:
        """Ensure calories are reasonable (0-5000)."""
        if v < 0:
            raise ValueError("Calories cannot be negative")
        if v > 5000:
            raise ValueError("Calories seem too high (>5000)")
        return v

    @field_validator("protein_g", "carbs_g", "fat_g")
    @classmethod
    def validate_macros(cls, v: float) -> float:
        """Ensure macros are reasonable (0-500g)."""
        if v < 0:
            raise ValueError("Macros cannot be negative")
        if v > 500:
            raise ValueError("Macro value seems too high (>500g)")
        return v


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
