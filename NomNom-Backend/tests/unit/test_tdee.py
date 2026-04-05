from src.services.profile_service import calculate_macro_targets, calculate_tdee


def test_tdee_male_sedentary():
    tdee = calculate_tdee(age=30, gender="male", height_cm=180, weight_kg=80, activity_level="sedentary")
    # BMR = 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    # TDEE = 1780 * 1.2 = 2136
    assert tdee == 2136


def test_tdee_female_moderate():
    tdee = calculate_tdee(age=25, gender="female", height_cm=165, weight_kg=60, activity_level="moderate")
    # BMR = 10*60 + 6.25*165 - 5*25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
    # TDEE = 1345.25 * 1.55 = 2085.14 -> 2085
    assert tdee == 2085


def test_tdee_unknown_activity_defaults_sedentary():
    tdee = calculate_tdee(age=30, gender="male", height_cm=180, weight_kg=80, activity_level="unknown")
    # Falls back to 1.2 multiplier (sedentary)
    assert tdee == 2136


def test_macro_targets_from_tdee():
    targets = calculate_macro_targets(2000)
    # Protein: 2000 * 0.30 / 4 = 150g
    assert targets.protein_target == 150
    # Carbs: 2000 * 0.40 / 4 = 200g
    assert targets.carb_target == 200
    # Fat: 2000 * 0.30 / 9 = 66.67 -> 67g
    assert targets.fat_target == 67
    assert targets.calorie_target == 2000
