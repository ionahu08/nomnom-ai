"""
Phase 5 Day 3: Meal Recommendation Workflow Implementation

Implements the workflow designed in Day 2:
1. Extract constraints (Haiku)
2. Search RAG (mock deterministic search)
3. Generate menus (Sonnet)
4. Validate (Opus)
5. Rank & explain (Sonnet)

This is a complete workflow example showing prompt chaining in action.
Run: python3 03_workflow_sandbox.py
"""

import json
import sys
from dataclasses import dataclass
from typing import Optional

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic library not installed")
    print("Install with: pip install anthropic")
    sys.exit(1)


# Mock food database (simulates RAG results)
MOCK_FOODS = [
    {"food_name": "Grilled Chicken Breast", "calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "allergens": [], "prep_time_min": 15},
    {"food_name": "Brown Rice", "calories": 220, "protein_g": 5, "carbs_g": 45, "fat_g": 2, "allergens": [], "prep_time_min": 30},
    {"food_name": "Quinoa", "calories": 222, "protein_g": 8, "carbs_g": 39, "fat_g": 4, "allergens": [], "prep_time_min": 20},
    {"food_name": "Mixed Green Salad", "calories": 50, "protein_g": 2, "carbs_g": 10, "fat_g": 0.5, "allergens": [], "prep_time_min": 5},
    {"food_name": "Broccoli", "calories": 55, "protein_g": 3.7, "carbs_g": 11, "fat_g": 0.6, "allergens": [], "prep_time_min": 10},
    {"food_name": "Salmon Fillet", "calories": 280, "protein_g": 25, "carbs_g": 0, "fat_g": 20, "allergens": ["fish"], "prep_time_min": 20},
    {"food_name": "Chickpeas", "calories": 270, "protein_g": 15, "carbs_g": 45, "fat_g": 4.3, "allergens": [], "prep_time_min": 5},
    {"food_name": "Sweet Potato", "calories": 103, "protein_g": 2, "carbs_g": 24, "fat_g": 0.1, "allergens": [], "prep_time_min": 45},
    {"food_name": "Greek Yogurt (plain, 1 cup)", "calories": 130, "protein_g": 23, "carbs_g": 9, "fat_g": 0.4, "allergens": ["dairy"], "prep_time_min": 0},
    {"food_name": "Hummus", "calories": 180, "protein_g": 6, "carbs_g": 16, "fat_g": 10, "allergens": ["sesame"], "prep_time_min": 0},
]


@dataclass
class DietaryConstraints:
    calorie_target: int
    calorie_tolerance: int
    allergies: list
    restrictions: list
    preferences: list
    meal_type: str


def step1_extract_constraints(user_input: str) -> Optional[DietaryConstraints]:
    """Step 1: Parse user input into structured constraints (Haiku)"""
    print("\n" + "="*70)
    print("STEP 1: Extract Constraints (Haiku)")
    print("="*70)
    print(f"Input: {user_input}\n")

    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"""Parse dietary requirements. Return ONLY valid JSON (no markdown):

{{
  "calorie_target": <int>,
  "calorie_tolerance": <int>,
  "allergies": [<string>, ...],
  "restrictions": [<string>, ...],
  "preferences": [<string>, ...],
  "meal_type": <string>
}}

User: "{user_input}"
"""
                }
            ],
        )

        json_str = response.content[0].text.strip()
        print(f"Output:\n{json_str}\n")

        data = json.loads(json_str)
        constraints = DietaryConstraints(
            calorie_target=data["calorie_target"],
            calorie_tolerance=data["calorie_tolerance"],
            allergies=data["allergies"],
            restrictions=data["restrictions"],
            preferences=data["preferences"],
            meal_type=data["meal_type"],
        )
        return constraints

    except Exception as e:
        print(f"ERROR in Step 1: {e}")
        return None


def step2_search_rag(constraints: DietaryConstraints) -> list:
    """Step 2: Mock RAG search (deterministic, no LLM)"""
    print("\n" + "="*70)
    print("STEP 2: Search RAG (Mock)")
    print("="*70)

    # Filter foods by constraints
    candidates = []
    for food in MOCK_FOODS:
        # Skip foods with user's allergens
        if any(allergen in food["allergens"] for allergen in constraints.allergies):
            continue
        candidates.append(food)

    print(f"Found {len(candidates)} foods matching constraints:")
    for food in candidates[:5]:
        print(f"  • {food['food_name']}: {food['calories']} cal, {food['protein_g']}g protein")
    print(f"  ... and {len(candidates) - 5} more\n")

    return candidates


def step3_generate_menus(constraints: DietaryConstraints, candidates: list) -> Optional[list]:
    """Step 3: Generate 3 candidate menus (Sonnet)"""
    print("\n" + "="*70)
    print("STEP 3: Generate Menus (Sonnet)")
    print("="*70)

    client = anthropic.Anthropic()

    candidates_str = json.dumps(candidates[:8], indent=2)  # Limit to 8 for token efficiency

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": f"""Generate 3 diverse lunch menus:
- Calorie target: {constraints.calorie_target} ± {constraints.calorie_tolerance}
- Allergies: {', '.join(constraints.allergies) if constraints.allergies else 'None'}
- Preferences: {', '.join(constraints.preferences) if constraints.preferences else 'None'}

Available foods:
{candidates_str}

Create 3 different menus (550-650 cal each). Include main + side + beverage.
Return ONLY valid JSON (no markdown):
[
  {{
    "menu_name": <string>,
    "dishes": [
      {{"food": <string>, "serving_size": <string>, "calories": <int>}}
    ],
    "total_calories": <int>,
    "prep_time_minutes": <int>,
    "appeal_reason": <string>
  }}
]
"""
                }
            ],
        )

        json_str = response.content[0].text.strip()
        menus = json.loads(json_str)
        print(f"Generated {len(menus)} menus:")
        for menu in menus:
            print(f"  • {menu['menu_name']}: {menu['total_calories']} cal\n")
        return menus

    except Exception as e:
        print(f"ERROR in Step 3: {e}")
        return None


def step4_validate(constraints: DietaryConstraints, menus: list) -> Optional[list]:
    """Step 4: Validate menus (Opus) - Safety critical"""
    print("\n" + "="*70)
    print("STEP 4: Validate Menus (Opus)")
    print("="*70)

    client = anthropic.Anthropic()
    menus_str = json.dumps(menus, indent=2)

    try:
        response = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Validate menus against constraints:
- Calorie target: {constraints.calorie_target} ± {constraints.calorie_tolerance}
- Allergies: {', '.join(constraints.allergies) if constraints.allergies else 'None'}

Menus:
{menus_str}

Check each for: calories in range, NO allergens, preferences met.
Return ONLY JSON:
[
  {{
    "menu_name": <string>,
    "passes_validation": <bool>,
    "issues": [<string>, ...],
    "confidence_score": <float 0-1>,
    "explanation": <string>
  }}
]
"""
                }
            ],
        )

        json_str = response.content[0].text.strip()
        validations = json.loads(json_str)

        passed = sum(1 for v in validations if v["passes_validation"])
        print(f"Validation complete: {passed}/{len(validations)} passed\n")
        for v in validations:
            status = "✓ PASS" if v["passes_validation"] else "✗ FAIL"
            print(f"  {status}: {v['menu_name']} (confidence: {v['confidence_score']})")
        print()

        return validations

    except Exception as e:
        print(f"ERROR in Step 4: {e}")
        return None


def step5_rank_and_explain(constraints: DietaryConstraints, menus: list, validations: list) -> Optional[dict]:
    """Step 5: Rank and explain best option (Sonnet)"""
    print("\n" + "="*70)
    print("STEP 5: Rank & Explain (Sonnet)")
    print("="*70)

    # Find passing menus
    ranked = []
    for menu, validation in zip(menus, validations):
        if validation["passes_validation"]:
            ranked.append({
                "menu": menu,
                "validation": validation,
                "score": validation["confidence_score"],
            })

    if not ranked:
        print("ERROR: No menus passed validation!")
        return None

    ranked.sort(key=lambda x: x["score"], reverse=True)
    ranked_str = json.dumps([r["menu"] for r in ranked], indent=2)

    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[
                {
                    "role": "user",
                    "content": f"""User asked for {constraints.calorie_target}-calorie {constraints.meal_type}.

Validated options:
{ranked_str}

Select the top choice and explain why. Include:
1. Rationale (why it's best)
2. Nutrition breakdown
3. Prep steps
4. Runner-up
5. NomNom's roasting comment (2-3 sentences, witty but friendly)

Return ONLY JSON:
{{
  "top_recommendation": <string>,
  "rationale": <string>,
  "nutrition_breakdown": {{"calories": <int>, "protein_g": <float>, "carbs_g": <float>, "fat_g": <float>}},
  "preparation_steps": [<string>, ...],
  "runner_up": <string or null>,
  "cat_commentary": <string>
}}
"""
                }
            ],
        )

        json_str = response.content[0].text.strip()
        result = json.loads(json_str)
        print(f"Top Recommendation: {result['top_recommendation']}\n")
        print(f"Rationale: {result['rationale']}\n")
        return result

    except Exception as e:
        print(f"ERROR in Step 5: {e}")
        return None


def run_workflow(user_input: str):
    """Execute the complete workflow"""
    print("\n" + "#"*70)
    print(f"# MEAL RECOMMENDATION WORKFLOW")
    print("#"*70)
    print(f"User input: {user_input}\n")

    # Step 1: Extract
    constraints = step1_extract_constraints(user_input)
    if not constraints:
        print("Workflow aborted at Step 1")
        return

    # Step 2: Search
    candidates = step2_search_rag(constraints)

    # Step 3: Generate
    menus = step3_generate_menus(constraints, candidates)
    if not menus:
        print("Workflow aborted at Step 3")
        return

    # Step 4: Validate
    validations = step4_validate(constraints, menus)
    if not validations:
        print("Workflow aborted at Step 4")
        return

    # Step 5: Rank & Explain
    recommendation = step5_rank_and_explain(constraints, menus, validations)
    if not recommendation:
        print("Workflow aborted at Step 5")
        return

    # Final output
    print("\n" + "#"*70)
    print("# FINAL RECOMMENDATION")
    print("#"*70)
    print(json.dumps(recommendation, indent=2))
    print("\n" + "#"*70)


if __name__ == "__main__":
    user_input = "I'm on a weight-loss diet and need a 600-calorie lunch. I'm allergic to peanuts and dairy."
    run_workflow(user_input)
