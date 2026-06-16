def get_nutrition_coach_prompt(context: dict) -> str:
    """
    Generate a customized system prompt for the nutrition coach.

    Args:
        context: Dictionary with user's nutrition data and health profile

    Returns:
        System prompt string customized to the user
    """

    # Build goal context
    goal_context = _get_goal_description(context.get("user_goal"))

    # Build nutrition summary
    nutrition_summary = _build_nutrition_summary(context)

    # Build constraints
    allergies = context.get("user_allergies") or []
    conditions = context.get("user_medical_conditions") or []

    allergies_str = ", ".join(allergies) if allergies else "none"
    conditions_str = ", ".join(conditions) if conditions else "none"

    # Build recent foods context
    foods = context.get("recent_foods") or []
    foods_str = ", ".join(foods[:10]) if foods else "no foods logged"

    system_prompt = f"""You are a friendly, knowledgeable nutrition coach for a food tracking app.
You help users understand their nutrition, improve their diet, and reach their health goals.

IMPORTANT RULES:
1. Be conversational and encouraging
2. Reference the user's actual food logs and nutrition data
3. Give specific, actionable advice
4. NEVER recommend foods that match their allergies or conflict with medical conditions
5. Keep responses concise (3-4 sentences max) for easy reading in a chat UI
6. Reference foods they've already logged when making suggestions

USER'S PROFILE:
- Goal: {goal_context}
- Age: {context.get('user_age', 'Not provided')}
- Allergies: {allergies_str}
- Medical Conditions: {conditions_str}

NUTRITION TARGETS:
- Calories: {context.get('calorie_target', 2000)} per day
- Protein: {context.get('protein_target', 150)}g per day
- Carbs: {context.get('carb_target', 200)}g per day
- Fat: {context.get('fat_target', 65)}g per day

THIS WEEK'S DATA:
{nutrition_summary}

RECENTLY LOGGED FOODS:
{foods_str}

STYLE:
- Be warm and supportive, not preachy
- Acknowledge their progress and effort
- Make suggestions based on their actual eating patterns
- Use their goal to personalize recommendations
- Keep it brief and actionable

Answer the user's question based on their specific situation and logged foods.
Always respect their allergies and medical conditions.
Reference their logged foods when possible to show you understand their eating patterns."""

    return system_prompt


def _get_goal_description(goal: str) -> str:
    """Convert goal code to human-readable description."""
    goal_map = {
        "maintain": "Maintain current weight and fitness level",
        "lean_out": "Reduce body fat while preserving muscle",
        "gain_muscle": "Build muscle mass",
        "lose_weight": "Lose weight",
    }
    return goal_map.get(goal, "Maintain health")


def _build_nutrition_summary(context: dict) -> str:
    """Build a summary of user's nutrition data for the past week."""
    days_logged = context.get("days_logged", 0)
    total_days = context.get("total_days", 7)

    # Calculate averages per day
    days_with_data = days_logged if days_logged > 0 else 1
    avg_calories = context.get("calories_this_week", 0) / days_with_data
    avg_protein = context.get("protein_this_week", 0) / days_with_data
    avg_carbs = context.get("carbs_this_week", 0) / days_with_data
    avg_fat = context.get("fat_this_week", 0) / days_with_data

    calorie_target = context.get("calorie_target", 2000)
    protein_target = context.get("protein_target", 150)
    carb_target = context.get("carb_target", 200)
    fat_target = context.get("fat_target", 65)

    # Calculate percentages
    calorie_pct = (avg_calories / calorie_target * 100) if calorie_target > 0 else 0
    protein_pct = (avg_protein / protein_target * 100) if protein_target > 0 else 0
    carb_pct = (avg_carbs / carb_target * 100) if carb_target > 0 else 0
    fat_pct = (avg_fat / fat_target * 100) if fat_target > 0 else 0

    summary = f"""Days logged: {days_logged}/{total_days}
Average daily intake:
- Calories: {avg_calories:.0f} ({calorie_pct:.0f}% of {calorie_target})
- Protein: {avg_protein:.0f}g ({protein_pct:.0f}% of {protein_target}g)
- Carbs: {avg_carbs:.0f}g ({carb_pct:.0f}% of {carb_target}g)
- Fat: {avg_fat:.0f}g ({fat_pct:.0f}% of {fat_target}g)"""

    return summary
