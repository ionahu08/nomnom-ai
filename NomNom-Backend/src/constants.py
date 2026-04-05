# Activity level multipliers for TDEE calculation
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# Default macro split (percentage of total calories)
DEFAULT_MACRO_SPLIT = {
    "protein": 0.30,  # 30% of calories from protein
    "carbs": 0.40,    # 40% of calories from carbs
    "fat": 0.30,      # 30% of calories from fat
}

# Calories per gram of each macro
CALORIES_PER_GRAM = {
    "protein": 4,
    "carbs": 4,
    "fat": 9,
}
