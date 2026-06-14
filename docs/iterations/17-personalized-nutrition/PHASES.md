# Iteration 17: Detailed Implementation Phases

---

## Phase 1: Backend Setup (Day 1)

### 1.1 Database Schema Design & Migration

**File:** `NomNom-Backend/alembic/versions/20260613_add_health_profile.py`

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON
import uuid

def upgrade():
    # Create ENUM types
    op.execute("""
        CREATE TYPE gender_enum AS ENUM ('male', 'female', 'other')
    """)
    op.execute("""
        CREATE TYPE goal_enum AS ENUM ('lose_weight', 'maintain', 'gain_muscle', 'shape_figure')
    """)
    op.execute("""
        CREATE TYPE activity_level_enum AS ENUM ('sedentary', 'light', 'moderate', 'active', 'very_active')
    """)
    
    # Create health_profile table
    op.create_table(
        'user_health_profile',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('gender', sa.Enum('male', 'female', 'other', name='gender_enum'), nullable=False),
        sa.Column('race', sa.String(50), nullable=True),
        sa.Column('height_cm', sa.Float, nullable=False),
        sa.Column('weight_kg', sa.Float, nullable=False),
        sa.Column('goal', sa.Enum('lose_weight', 'maintain', 'gain_muscle', 'shape_figure', name='goal_enum'), nullable=False),
        sa.Column('activity_level', sa.Enum('sedentary', 'light', 'moderate', 'active', 'very_active', name='activity_level_enum'), nullable=False),
        sa.Column('allergies', JSON, nullable=True, default=[]),
        sa.Column('medical_conditions', JSON, nullable=True, default=[]),
        sa.Column('surgeries', JSON, nullable=True, default=[]),
        sa.Column('medications', JSON, nullable=True, default=[]),
        sa.Column('daily_calorie_target', sa.Integer, nullable=False),
        sa.Column('daily_protein_g', sa.Integer, nullable=False),
        sa.Column('daily_carbs_g', sa.Integer, nullable=False),
        sa.Column('daily_fat_g', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    op.create_index('ix_user_health_profile_user_id', 'user_health_profile', ['user_id'])

def downgrade():
    op.drop_table('user_health_profile')
    op.execute("DROP TYPE activity_level_enum")
    op.execute("DROP TYPE goal_enum")
    op.execute("DROP TYPE gender_enum")
```

**Run migration:**
```bash
cd NomNom-Backend
alembic upgrade head
```

**Verify:**
```bash
psql $DATABASE_URL -c "\d user_health_profile"
```

---

### 1.2 SQLAlchemy ORM Models

**File:** `NomNom-Backend/src/models/health_profile.py`

```python
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class GoalEnum(str, Enum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN = "maintain"
    GAIN_MUSCLE = "gain_muscle"
    SHAPE_FIGURE = "shape_figure"

class ActivityLevelEnum(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class HealthProfile(Base):
    __tablename__ = "user_health_profile"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Demographic
    age = Column(Integer, nullable=False)
    gender = Column(SQLEnum(GenderEnum), nullable=False)
    race = Column(String(50), nullable=True)
    
    # Anthropometric
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    
    # Goals & Activity
    goal = Column(SQLEnum(GoalEnum), nullable=False)
    activity_level = Column(SQLEnum(ActivityLevelEnum), nullable=False)
    
    # Medical
    allergies = Column(JSON, nullable=True, default=[])
    medical_conditions = Column(JSON, nullable=True, default=[])
    surgeries = Column(JSON, nullable=True, default=[])
    medications = Column(JSON, nullable=True, default=[])
    
    # Calculated targets
    daily_calorie_target = Column(Integer, nullable=False)
    daily_protein_g = Column(Integer, nullable=False)
    daily_carbs_g = Column(Integer, nullable=False)
    daily_fat_g = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="health_profile")
```

**Update:** `NomNom-Backend/src/models/user.py`
```python
health_profile = relationship("HealthProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
```

---

### 1.3 Pydantic Schemas

**File:** `NomNom-Backend/src/schemas/health_profile.py`

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
from datetime import datetime

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class GoalEnum(str, Enum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN = "maintain"
    GAIN_MUSCLE = "gain_muscle"
    SHAPE_FIGURE = "shape_figure"

class ActivityLevelEnum(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class HealthProfileCreate(BaseModel):
    age: int = Field(..., ge=18, le=120)
    gender: GenderEnum
    race: Optional[str] = None
    height_cm: float = Field(..., ge=100, le=250)
    weight_kg: float = Field(..., ge=30, le=300)
    goal: GoalEnum
    activity_level: ActivityLevelEnum
    allergies: List[str] = []
    medical_conditions: List[str] = []
    surgeries: List[str] = []
    medications: List[str] = []

class HealthProfileUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[GenderEnum] = None
    race: Optional[str] = None
    height_cm: Optional[float] = Field(None, ge=100, le=250)
    weight_kg: Optional[float] = Field(None, ge=30, le=300)
    goal: Optional[GoalEnum] = None
    activity_level: Optional[ActivityLevelEnum] = None
    allergies: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    surgeries: Optional[List[str]] = None
    medications: Optional[List[str]] = None

class HealthProfileResponse(BaseModel):
    id: str
    user_id: str
    age: int
    gender: GenderEnum
    race: Optional[str]
    height_cm: float
    weight_kg: float
    goal: GoalEnum
    activity_level: ActivityLevelEnum
    daily_calorie_target: int
    daily_protein_g: int
    daily_carbs_g: int
    daily_fat_g: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

---

### 1.4 Nutrition Calculation Service

**File:** `NomNom-Backend/src/services/nutrition_service.py`

```python
from typing import Dict, List
from src.schemas.health_profile import GoalEnum, ActivityLevelEnum

class NutritionService:
    @staticmethod
    def calculate_bmr(age: int, gender: str, weight_kg: float, height_cm: float) -> float:
        """
        Mifflin-St Jeor Formula for Basal Metabolic Rate
        Formula: (10 × weight) + (6.25 × height) - (5 × age) + sex_offset
        where sex_offset = 5 for men, -161 for women
        """
        sex_offset = 5 if gender == "male" else -161
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + sex_offset
        return round(bmr, 2)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Total Daily Energy Expenditure = BMR × activity_multiplier
        """
        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        multiplier = multipliers.get(activity_level, 1.55)
        tdee = bmr * multiplier
        return round(tdee, 2)
    
    @staticmethod
    def adjust_tdee_by_goal(tdee: float, goal: str, weight_kg: float) -> float:
        """
        Adjust TDEE based on fitness goal
        """
        adjustments = {
            "lose_weight": 0.85,      # 500 kcal deficit ≈ 0.5kg/week loss
            "maintain": 1.0,
            "gain_muscle": 1.1,       # 250 kcal surplus
            "shape_figure": 0.95,     # 250 kcal deficit (preserve muscle)
        }
        multiplier = adjustments.get(goal, 1.0)
        adjusted_tdee = tdee * multiplier
        return round(adjusted_tdee, 2)
    
    @staticmethod
    def calculate_macros(adjusted_tdee: float, goal: str) -> Dict[str, int]:
        """
        Calculate macronutrient distribution based on goal
        Returns: {protein_g, carbs_g, fat_g}
        """
        macro_splits = {
            "lose_weight": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
            "maintain": {"protein": 0.25, "carbs": 0.50, "fat": 0.25},
            "gain_muscle": {"protein": 0.35, "carbs": 0.45, "fat": 0.20},
            "shape_figure": {"protein": 0.35, "carbs": 0.40, "fat": 0.25},
        }
        
        split = macro_splits.get(goal, macro_splits["maintain"])
        
        protein_g = round((adjusted_tdee * split["protein"]) / 4)  # 4 kcal/g
        carbs_g = round((adjusted_tdee * split["carbs"]) / 4)      # 4 kcal/g
        fat_g = round((adjusted_tdee * split["fat"]) / 9)          # 9 kcal/g
        
        return {
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
        }
    
    @staticmethod
    def validate_health_profile(age: int, height_cm: float, weight_kg: float, 
                               goal: str, activity_level: str) -> List[str]:
        """
        Validate health profile data. Returns list of error messages (empty if valid).
        """
        errors = []
        
        if not (18 <= age <= 120):
            errors.append("Age must be between 18 and 120")
        
        if not (100 <= height_cm <= 250):
            errors.append("Height must be between 100 and 250 cm")
        
        if not (30 <= weight_kg <= 300):
            errors.append("Weight must be between 30 and 300 kg")
        
        # BMI sanity check
        bmi = weight_kg / ((height_cm / 100) ** 2)
        if bmi < 15 or bmi > 50:
            errors.append(f"BMI {bmi:.1f} seems unusual. Please double-check your measurements.")
        
        # Goal + Activity sanity check
        if goal == "gain_muscle" and activity_level == "sedentary":
            errors.append("Sedentary activity level is unsuitable for muscle gain goal. Consider 'light' or higher.")
        
        return errors
    
    @staticmethod
    def calculate_daily_targets(age: int, gender: str, height_cm: float, weight_kg: float,
                               goal: str, activity_level: str) -> Dict[str, int]:
        """
        All-in-one calculation: BMR → TDEE → adjust by goal → calculate macros
        Returns: {daily_calorie_target, daily_protein_g, daily_carbs_g, daily_fat_g}
        """
        bmr = NutritionService.calculate_bmr(age, gender, weight_kg, height_cm)
        tdee = NutritionService.calculate_tdee(bmr, activity_level)
        adjusted_tdee = NutritionService.adjust_tdee_by_goal(tdee, goal, weight_kg)
        macros = NutritionService.calculate_macros(adjusted_tdee, goal)
        
        return {
            "daily_calorie_target": int(adjusted_tdee),
            "daily_protein_g": macros["protein_g"],
            "daily_carbs_g": macros["carbs_g"],
            "daily_fat_g": macros["fat_g"],
        }
```

**Unit Tests:** `NomNom-Backend/tests/services/test_nutrition_service.py`

```python
import pytest
from src.services.nutrition_service import NutritionService

def test_calculate_bmr_male():
    # 30-year-old male, 75kg, 175cm
    bmr = NutritionService.calculate_bmr(age=30, gender="male", weight_kg=75, height_cm=175)
    assert 1650 < bmr < 1750  # Expect ~1700

def test_calculate_bmr_female():
    # 25-year-old female, 60kg, 165cm
    bmr = NutritionService.calculate_bmr(age=25, gender="female", weight_kg=60, height_cm=165)
    assert 1300 < bmr < 1400  # Expect ~1350

def test_calculate_tdee():
    bmr = 1700
    tdee = NutritionService.calculate_tdee(bmr, "moderate")
    assert tdee == 1700 * 1.55
    assert tdee == 2635

def test_adjust_tdee_by_goal():
    tdee = 2635
    adjusted = NutritionService.adjust_tdee_by_goal(tdee, "lose_weight", 75)
    assert adjusted == int(2635 * 0.85)

def test_calculate_macros():
    adjusted_tdee = 2240
    macros = NutritionService.calculate_macros(adjusted_tdee, "lose_weight")
    # lose_weight: 30% protein, 40% carbs, 30% fat
    assert 160 < macros["protein_g"] < 175
    assert 220 < macros["carbs_g"] < 230
    assert 70 < macros["fat_g"] < 80

def test_validate_health_profile_valid():
    errors = NutritionService.validate_health_profile(
        age=30, height_cm=175, weight_kg=75, goal="lose_weight", activity_level="moderate"
    )
    assert errors == []

def test_validate_health_profile_invalid_age():
    errors = NutritionService.validate_health_profile(
        age=15, height_cm=175, weight_kg=75, goal="lose_weight", activity_level="moderate"
    )
    assert "Age must be between 18 and 120" in errors

def test_validate_health_profile_suspicious_bmi():
    errors = NutritionService.validate_health_profile(
        age=30, height_cm=175, weight_kg=500, goal="lose_weight", activity_level="moderate"
    )
    assert any("BMI" in error for error in errors)

def test_calculate_daily_targets():
    targets = NutritionService.calculate_daily_targets(
        age=30, gender="male", height_cm=175, weight_kg=75,
        goal="lose_weight", activity_level="moderate"
    )
    assert targets["daily_calorie_target"] > 0
    assert targets["daily_protein_g"] > 0
    assert targets["daily_carbs_g"] > 0
    assert targets["daily_fat_g"] > 0
    # Rough check: calories should be between 1800-2500 for this profile
    assert 1800 < targets["daily_calorie_target"] < 2500

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Phase 2: Backend APIs (Day 2)

### 2.1 API Endpoints

**File:** `NomNom-Backend/src/api/user.py` (add these endpoints)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.health_profile import HealthProfileCreate, HealthProfileUpdate, HealthProfileResponse
from src.models.health_profile import HealthProfile
from src.services.nutrition_service import NutritionService
from src.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/user", tags=["user"])

@router.post("/health-profile", response_model=HealthProfileResponse)
async def create_health_profile(
    profile_data: HealthProfileCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user's health profile and calculate daily nutrition targets."""
    
    # Validate input
    errors = NutritionService.validate_health_profile(
        profile_data.age,
        profile_data.height_cm,
        profile_data.weight_kg,
        profile_data.goal,
        profile_data.activity_level
    )
    if errors:
        raise HTTPException(status_code=400, detail={"validation_errors": errors})
    
    # Calculate daily targets
    targets = NutritionService.calculate_daily_targets(
        age=profile_data.age,
        gender=profile_data.gender,
        height_cm=profile_data.height_cm,
        weight_kg=profile_data.weight_kg,
        goal=profile_data.goal,
        activity_level=profile_data.activity_level
    )
    
    # Check if health profile exists
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if health_profile:
        # Update existing
        health_profile.age = profile_data.age
        health_profile.gender = profile_data.gender
        health_profile.race = profile_data.race
        health_profile.height_cm = profile_data.height_cm
        health_profile.weight_kg = profile_data.weight_kg
        health_profile.goal = profile_data.goal
        health_profile.activity_level = profile_data.activity_level
        health_profile.allergies = profile_data.allergies
        health_profile.medical_conditions = profile_data.medical_conditions
        health_profile.surgeries = profile_data.surgeries
        health_profile.medications = profile_data.medications
        health_profile.daily_calorie_target = targets["daily_calorie_target"]
        health_profile.daily_protein_g = targets["daily_protein_g"]
        health_profile.daily_carbs_g = targets["daily_carbs_g"]
        health_profile.daily_fat_g = targets["daily_fat_g"]
    else:
        # Create new
        health_profile = HealthProfile(
            user_id=current_user.id,
            age=profile_data.age,
            gender=profile_data.gender,
            race=profile_data.race,
            height_cm=profile_data.height_cm,
            weight_kg=profile_data.weight_kg,
            goal=profile_data.goal,
            activity_level=profile_data.activity_level,
            allergies=profile_data.allergies,
            medical_conditions=profile_data.medical_conditions,
            surgeries=profile_data.surgeries,
            medications=profile_data.medications,
            **targets
        )
        db.add(health_profile)
    
    db.commit()
    db.refresh(health_profile)
    return health_profile

@router.get("/health-profile", response_model=HealthProfileResponse)
async def get_health_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's health profile."""
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not health_profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    return health_profile

@router.patch("/health-profile", response_model=HealthProfileResponse)
async def update_health_profile(
    profile_update: HealthProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Partially update user's health profile."""
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not health_profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    # Prepare update data
    update_data = profile_update.dict(exclude_unset=True)
    
    # If any calculation-relevant field is updated, recalculate targets
    needs_recalc = any(
        field in update_data for field in 
        ["age", "gender", "height_cm", "weight_kg", "goal", "activity_level"]
    )
    
    if needs_recalc:
        # Use current values + updates for calculation
        age = update_data.get("age", health_profile.age)
        gender = update_data.get("gender", health_profile.gender)
        height_cm = update_data.get("height_cm", health_profile.height_cm)
        weight_kg = update_data.get("weight_kg", health_profile.weight_kg)
        goal = update_data.get("goal", health_profile.goal)
        activity_level = update_data.get("activity_level", health_profile.activity_level)
        
        # Validate
        errors = NutritionService.validate_health_profile(age, height_cm, weight_kg, goal, activity_level)
        if errors:
            raise HTTPException(status_code=400, detail={"validation_errors": errors})
        
        # Recalculate
        targets = NutritionService.calculate_daily_targets(
            age, gender, height_cm, weight_kg, goal, activity_level
        )
        update_data.update(targets)
    
    # Apply updates
    for field, value in update_data.items():
        setattr(health_profile, field, value)
    
    db.commit()
    db.refresh(health_profile)
    return health_profile
```

---

### 2.2 Integration Tests

**File:** `NomNom-Backend/tests/api/test_health_profile.py`

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_health_profile(auth_headers):
    payload = {
        "age": 30,
        "gender": "male",
        "race": "Asian",
        "height_cm": 175.0,
        "weight_kg": 75.0,
        "goal": "lose_weight",
        "activity_level": "moderate",
        "allergies": ["peanuts"],
        "medical_conditions": ["pre_diabetes"],
        "surgeries": [],
        "medications": ["metformin"]
    }
    
    response = client.post(
        "/api/v1/user/health-profile",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 30
    assert data["daily_calorie_target"] > 0
    assert data["daily_protein_g"] > 0

def test_get_health_profile(auth_headers):
    # First create
    payload = {"age": 30, "gender": "male", ...}  # Same as above
    client.post("/api/v1/user/health-profile", json=payload, headers=auth_headers)
    
    # Then get
    response = client.get("/api/v1/user/health-profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 30

def test_update_health_profile(auth_headers):
    # Create
    payload = {"age": 30, "gender": "male", ...}
    client.post("/api/v1/user/health-profile", json=payload, headers=auth_headers)
    
    # Update weight
    update_payload = {"weight_kg": 70.0}
    response = client.patch(
        "/api/v1/user/health-profile",
        json=update_payload,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["weight_kg"] == 70.0
    # Targets should be recalculated
    assert data["daily_calorie_target"] > 0

def test_validation_invalid_age(auth_headers):
    payload = {"age": 15, "gender": "male", ...}  # Too young
    response = client.post(
        "/api/v1/user/health-profile",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Age" in response.json()["detail"]["validation_errors"][0]
```

---

## Phase 3: iOS Settings Screen (Day 3)

### 3.1 Health Profile View

**File:** `NomNom-iOS/NomNom/Features/Settings/HealthProfileView.swift`

```swift
import SwiftUI

struct HealthProfileView: View {
    @StateObject private var viewModel = HealthProfileViewModel()
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            Form {
                // MARK: - Basic Information
                Section("Basic Information") {
                    Stepper("Age: \(viewModel.age)", value: $viewModel.age, in: 18...120)
                    
                    Picker("Gender", selection: $viewModel.gender) {
                        ForEach(GenderOption.allCases, id: \.self) { option in
                            Text(option.rawValue.capitalized).tag(option)
                        }
                    }
                    
                    TextField("Race (Optional)", text: $viewModel.race)
                }
                
                // MARK: - Anthropometric Data
                Section("Measurements") {
                    HStack {
                        Text("Height")
                        Spacer()
                        TextField("cm", text: $viewModel.heightCM)
                            .keyboardType(.decimalPad)
                            .frame(width: 80)
                    }
                    
                    HStack {
                        Text("Weight")
                        Spacer()
                        TextField("kg", text: $viewModel.weightKG)
                            .keyboardType(.decimalPad)
                            .frame(width: 80)
                    }
                    
                    if let bmi = viewModel.calculateBMI() {
                        HStack {
                            Text("BMI")
                            Spacer()
                            Text(String(format: "%.1f", bmi))
                                .foregroundColor(bmiColor(for: bmi))
                                .fontWeight(.semibold)
                        }
                    }
                }
                
                // MARK: - Fitness Goals
                Section("Goals & Activity") {
                    Picker("Goal", selection: $viewModel.goal) {
                        ForEach(GoalOption.allCases, id: \.self) { option in
                            Text(option.displayName).tag(option)
                        }
                    }
                    
                    Picker("Activity Level", selection: $viewModel.activityLevel) {
                        ForEach(ActivityLevelOption.allCases, id: \.self) { option in
                            Text(option.displayName).tag(option)
                        }
                    }
                }
                
                // MARK: - Medical Information
                Section {
                    NavigationLink(destination: MedicalInfoView(viewModel: viewModel)) {
                        HStack {
                            Text("Medical Information")
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.gray)
                        }
                    }
                } header: {
                    Text("Medical Information (Optional)")
                } footer: {
                    Text("Helps us provide safer recommendations")
                }
                
                // MARK: - Daily Targets (Summary Card)
                Section("Daily Targets") {
                    VStack(alignment: .leading, spacing: 12) {
                        if let targets = viewModel.calculateTargets() {
                            TargetRow(icon: "🔥", label: "Calories", value: "\(targets.calorieTarget) kcal")
                            TargetRow(icon: "🥩", label: "Protein", value: "\(targets.proteinG)g")
                            TargetRow(icon: "🍞", label: "Carbs", value: "\(targets.carbsG)g")
                            TargetRow(icon: "🧈", label: "Fat", value: "\(targets.fatG)g")
                        } else {
                            Text("Fill in all fields to see targets")
                                .foregroundColor(.gray)
                        }
                    }
                    .padding(.vertical, 8)
                }
            }
            .navigationTitle("Health Profile")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        viewModel.save() {
                            dismiss()
                        }
                    }
                    .disabled(!viewModel.isValid)
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func bmiColor(for bmi: Double) -> Color {
        if bmi < 18.5 {
            return .blue
        } else if bmi < 25 {
            return .green
        } else if bmi < 30 {
            return .orange
        } else {
            return .red
        }
    }
}

struct TargetRow: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(icon).font(.title3)
            Text(label)
            Spacer()
            Text(value).fontWeight(.semibold)
        }
    }
}

#Preview {
    HealthProfileView()
}
```

---

## Phase 4: iOS Food Diary Integration (Day 4)

### 4.1 Daily Summary Component

Update `FoodDiaryView.swift` to show daily summary with targets and progress bars.

---

## Phase 5: Testing & Documentation (Day 5)

Create comprehensive test suite and iteration summary.

---

**Total Effort:**
- Day 1: Database + service (3–4 hours)
- Day 2: Backend APIs + tests (3–4 hours)
- Day 3: iOS Settings form (4–5 hours)
- Day 4: iOS integration (3–4 hours)
- Day 5: Testing + docs (2–3 hours)

**Total: ~20 hours over 5 days**
