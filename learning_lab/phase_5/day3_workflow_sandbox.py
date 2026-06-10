"""
Day 3: Meal Recommendation Workflow Implementation

Implements the workflow designed in Day 2:
1. Extract constraints (Haiku)
2. Search RAG (deterministic)
3. Generate menus (Sonnet)
4. Validate (Opus)
5. Rank & explain (Sonnet)

This is a complete workflow example showing prompt chaining in action.
"""

import json
from dataclasses import dataclass
from typing import Optional
import anthropic

# Initialize client
client = anthropic.Anthropic()

# Sample food database (simulating RAG results)
SAMPLE_FOODS = [
    {
        "food_name": "Grilled Chicken Breast",
        "calories": 165,
        "protein_g": 31,
        "carbs_g": 0,
        "fat_g": 3.6,
        "allergens": [],
        "prep_time_min": 15,
    },
    {
        "food_name": "Brown Rice",
        "calories": 220,
        "protein_g": 5,
        "carbs_g": 45,
        "fat_g": 2,
        "allergens": [],
        "prep_time_min": 30,
    },
    {
        "food_name": "Mixed Green Salad",
        "calories": 50,
        "protein_g": 2,
        "carbs_g": 10,
        "fat_g": 0.5,
        "allergens": [],
        "prep_time_min": 5,
    },
    {
        "food_name": "Quinoa",
        "calories": 222,
        "protein_g": 8,
        "carbs_g": 39,
        "fat_g": 4,
        "allergens": [],
        "prep_time_min": 20,
    },
    {
        "food_name": "Salmon Fillet",
        "calories": 280,
        "protein_g": 25,
        "carbs_g": 0,
        "fat_g": 20,
        "allergens": ["fish"],
        "prep_time_min": 20,
    },
    {
        "food_name": "Chickpeas",
        "calories": 270,
        "protein_g": 15,
        "carbs_g": 45,
        "fat_g": 4.3,
        "allergens": [],
        "prep_time_min": 5,  # canned
    },
    {
        "food_name": "Broccoli",
        "calories": 55,
        "protein_g": 3.7,
        "carbs_g": 11,
        "fat_g": 0.6,
        "allergens": [],
        "prep_time_min": 10,
    },
    {
        "food_name": "Sweet Potato",
        "calories": 103,
        "protein_g": 2,
        "carbs_g": 24,
        "fat_g": 0.1,
        "allergens": [],
        "prep_time_min": 45,
    },
]

@dataclass
class DietaryConstraints:
    calorie_target: int
    calorie_tolerance: int
    allergies: list[str]
    restrictions: list[str]
    preferences: list[str]
    meal_type: str


def step1_extract_constraints(user_input: str) -> DietaryConstraints:
    """
    Step 1: Parse user input into structured constraints.
    Uses Haiku for cost savings (simple classification).
    """
    print("\n=== Step 1: Extract Constraints (Haiku) ===")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""Parse dietary requirements from user request. Return ONLY valid JSON.

User request: "{user_input}"

Return JSON (no markdown, no explanation):
{{
  "calorie_target": <int>,
  "calorie_tolerance": <int>,
  "allergies": [<string>, ...],
  "restrictions": [<string>, ...],
  "preferences": [<string>, ...],
  "meal_type": <string>
}}""",
            }
        ],
    )

    json_str = response.content[0].text.strip()
    print(f"Extracted: {json_str}")
    data = json.loads(json_str)

    return DietaryConstraints(
        calorie_target=data["calorie_target"],
        calorie_tolerance=data["calorie_tolerance"],
        allergies=data["allergies"],
        restrictions=data["restrictions"],
        preferences=data["preferences"],
        meal_type=data["meal_type"],
    )


def step2_search_rag(constraints: DietaryConstraints) -> list[dict]:
    """
    Step 2: Retrieve foods matching constraints.
    In production, this queries the RAG vector store.
    Here, we filter the sample database.
    """
    print("\n=== Step 2: Search RAG ===")

    # Filter foods by constraints
    candidates = []
    for food in SAMPLE_FOODS:
        # Check allergens
        has_allergen = any(allergen in food["allergens"] for allergen in constraints.allergies)
        if has_allergen:
            continue

        # Return top 8 candidates
        candidates.append(food)

    print(f"Found {len(candidates)} foods matching constraints")
    for food in candidates:
        print(f"  - {food['food_name']}: {food['calories']} cal")

    return candidates


def step3_generate_menus(constraints: DietaryConstraints, candidates: list[dict]) -> list[dict]:
    """
    Step 3: Generate 3 candidate menus.
    Uses Sonnet for creativity and reasoning.
    """
    print("\n=== Step 3: Generate Menus (Sonnet) ===")

    candidates_str = json.dumps(candidates, indent=2)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""Generate 3 diverse lunch menus within these constraints:
- Calorie target: {constraints.calorie_target} ± {constraints.calorie_tolerance}
- Allergies: {', '.join(constraints.allergies) if constraints.allergies else 'None'}
- Preferences: {', '.join(constraints.preferences) if constraints.preferences else 'None'}

Available foods:
{candidates_str}

Create 3 different, appealing menus. Each should:
1. Total 550–650 calories
2. Include main + side + beverage (or logical combination)
3. Be diverse (different styles)
4. Use ONLY foods from the list above

Return ONLY valid JSON array (no markdown):
[
  {{
    "menu_name": <string>,
    "dishes": [
      {{"food": <string>, "serving_size": <string>, "calories": <int>}},
      ...
    ],
    "total_calories": <int>,
    "prep_time_minutes": <int>,
    "appeal_reason": <string>
  }}
]""",
            }
        ],
    )

    json_str = response.content[0].text.strip()
    print(f"Generated menus:\n{json_str}")
    menus = json.loads(json_str)

    return menus


def step4_validate(constraints: DietaryConstraints, menus: list[dict]) -> list[dict]:
    """
    Step 4: Validate menus against constraints.
    Uses Opus for critical judgment (allergen safety).
    """
    print("\n=== Step 4: Validate Menus (Opus) ===")

    menus_str = json.dumps(menus, indent=2)

    response = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""Validate these menus against constraints:
- Calorie target: {constraints.calorie_target} ± {constraints.calorie_tolerance}
- Allergies: {', '.join(constraints.allergies) if constraints.allergies else 'None'}

Menus:
{menus_str}

For EACH menu:
1. Check calories are in range
2. Check NO allergens present
3. List any issues found

Return ONLY valid JSON (no markdown):
[
  {{
    "menu_name": <string>,
    "passes_validation": <bool>,
    "issues": [<string>, ...],
    "confidence_score": <float>,
    "explanation": <string>
  }}
]""",
            }
        ],
    )

    json_str = response.content[0].text.strip()
    print(f"Validation results:\n{json_str}")
    validations = json.loads(json_str)

    return validations


def step5_rank_and_explain(
    constraints: DietaryConstraints,
    menus: list[dict],
    validations: list[dict],
) -> dict:
    """
    Step 5: Rank and explain the best option.
    Uses Sonnet for synthesis and natural explanation.
    """
    print("\n=== Step 5: Rank & Explain (Sonnet) ===")

    # Combine menus with validation results
    ranked = []
    for menu, validation in zip(menus, validations):
        if validation["passes_validation"]:
            ranked.append({
                "menu": menu,
                "validation": validation,
                "score": validation["confidence_score"],
            })

    if not ranked:
        print("ERROR: No valid menus!")
        return {"error": "No menus passed validation"}

    ranked.sort(key=lambda x: x["score"], reverse=True)
    top_menu = ranked[0]
    runner_up = ranked[1] if len(ranked) > 1 else None

    ranked_str = json.dumps([r["menu"] for r in ranked], indent=2)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": f"""The user asked for a {constraints.calorie_target}-calorie {constraints.meal_type}.

Here are validated menu options:
{ranked_str}

Select the best one and explain:
1. Why it's best for their constraints
2. Nutritional breakdown
3. How to prepare
4. Runner-up if available
5. Add a witty NomNom cat comment (2-3 sentences, roasting but friendly)

Return ONLY valid JSON (no markdown):
{{
  "top_recommendation": <string>,
  "rationale": <string>,
  "nutrition": {{
    "calories": <int>,
    "protein_g": <float>,
    "carbs_g": <float>,
    "fat_g": <float>
  }},
  "preparation": [<string>, ...],
  "runner_up": <string or null>,
  "cat_commentary": <string>
}}""",
            }
        ],
    )

    json_str = response.content[0].text.strip()
    print(f"Final recommendation:\n{json_str}")
    result = json.loads(json_str)

    return result


def run_workflow(user_input: str):
    """Execute the complete meal recommendation workflow."""
    print(f"\n{'='*60}")
    print(f"USER INPUT: {user_input}")
    print(f"{'='*60}")

    # Step 1: Extract constraints
    constraints = step1_extract_constraints(user_input)
    print(f"Constraints: {constraints}")

    # Step 2: Search RAG
    candidates = step2_search_rag(constraints)

    # Step 3: Generate menus
    menus = step3_generate_menus(constraints, candidates)

    # Step 4: Validate
    validations = step4_validate(constraints, menus)

    # Step 5: Rank & explain
    recommendation = step5_rank_and_explain(constraints, menus, validations)

    print(f"\n{'='*60}")
    print("FINAL RECOMMENDATION:")
    print(f"{'='*60}")
    print(json.dumps(recommendation, indent=2))

    return recommendation


if __name__ == "__main__":
    # Test the workflow with a sample user input
    user_input = "I'm on a weight-loss diet and need a 600-calorie lunch. I'm allergic to peanuts and dairy."

    recommendation = run_workflow(user_input)
