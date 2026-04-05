from pydantic import BaseModel


class ProfileCreate(BaseModel):
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str
    cat_style: str = "sassy"
    allergies: list[str] | None = None
    dietary_restrictions: list[str] | None = None
    cuisine_preferences: list[str] | None = None


class ProfileUpdate(BaseModel):
    age: int | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    activity_level: str | None = None
    cat_style: str | None = None
    allergies: list[str] | None = None
    dietary_restrictions: list[str] | None = None
    cuisine_preferences: list[str] | None = None
    calorie_target: int | None = None
    protein_target: int | None = None
    carb_target: int | None = None
    fat_target: int | None = None
    notification_enabled: bool | None = None


class MacroTargets(BaseModel):
    calorie_target: int
    protein_target: int
    carb_target: int
    fat_target: int


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str
    cat_style: str
    allergies: list[str] | None
    dietary_restrictions: list[str] | None
    cuisine_preferences: list[str] | None
    calorie_target: int | None
    protein_target: int | None
    carb_target: int | None
    fat_target: int | None
    notification_enabled: bool
    targets: MacroTargets

    model_config = {"from_attributes": True}
