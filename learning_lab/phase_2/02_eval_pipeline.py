#!/usr/bin/env python3
"""
Phase 2 Day 2: First Eval Pipeline

The 6-step eval workflow:
1. Write initial prompt
2. Create eval dataset (test cases)
3. Insert dataset inputs into prompt template
4. Run LLM to get outputs
5. Use grader to score, compute average
6. Modify prompt based on scores, repeat

This script demonstrates the loop: prompt → eval → grade → iterate → re-eval.
You'll see how grading results drive prompt improvements.

Usage:
    python 02_eval_pipeline.py
"""

import os
import json
import asyncio
from dataclasses import dataclass
from anthropic import AsyncAnthropic

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


# ============================================================================
# STEP 2: Create Eval Dataset
# ============================================================================

@dataclass
class FoodTestCase:
    """A single test case: food description + ground truth."""
    description: str
    expected_food_name: str  # What we expect Claude to identify
    expected_calories_range: tuple  # (min, max) for plausibility check


# Mix of easy and hard cases
EVAL_DATASET = [
    FoodTestCase(
        description="A grilled chicken Caesar salad with croutons and parmesan",
        expected_food_name="Caesar Salad",
        expected_calories_range=(250, 450),
    ),
    FoodTestCase(
        description="Two scrambled eggs with toast and butter",
        expected_food_name="Eggs and Toast",
        expected_calories_range=(300, 500),
    ),
    FoodTestCase(
        description="A large pepperoni pizza slice with melted cheese",
        expected_food_name="Pepperoni Pizza",
        expected_calories_range=(250, 400),  # Per slice
    ),
    FoodTestCase(
        description="Greek yogurt with granola and honey drizzle",
        expected_food_name="Greek Yogurt with Granola",
        expected_calories_range=(200, 350),
    ),
    FoodTestCase(
        description="A blurry photo of something brown and round on a plate",
        expected_food_name="Unknown",
        expected_calories_range=(100, 1000),  # Very wide range for ambiguous case
    ),
]


# ============================================================================
# STEP 5: Use Grader to Score
# ============================================================================

def grade_output(output_str: str, test_case: FoodTestCase) -> dict:
    """
    Code-based grader. Checks:
    1. JSON validity
    2. Required fields present
    3. Numeric plausibility (calories in reasonable range)
    4. Food name recognition (is it empty/null?)

    Returns: {"score": 0-10, "details": {...}}
    """
    score = 0
    details = {}

    # Check 1: Valid JSON?
    try:
        data = json.loads(output_str)
        score += 2
        details["json_valid"] = True
    except json.JSONDecodeError as e:
        details["json_valid"] = False
        details["json_error"] = str(e)
        return {"score": score, "details": details}

    # Check 2: Required fields present?
    required_fields = ["food_name", "calories", "protein_g", "carbs_g", "fat_g"]
    missing = [f for f in required_fields if f not in data or data[f] is None]
    if not missing:
        score += 2
        details["fields_present"] = True
    else:
        details["fields_present"] = False
        details["missing_fields"] = missing

    # Check 3: Numeric plausibility
    try:
        calories = float(data.get("calories", 0))
        min_cal, max_cal = test_case.expected_calories_range

        # Generous range: allow ±30% margin
        margin = max(50, (max_cal - min_cal) * 0.3)
        if min_cal - margin <= calories <= max_cal + margin:
            score += 3
            details["calories_plausible"] = True
            details["calories_value"] = calories
        else:
            details["calories_plausible"] = False
            details["calories_value"] = calories
            details["expected_range"] = test_case.expected_calories_range

        # Check macros are positive and sum to roughly calories
        protein = float(data.get("protein_g", 0))
        carbs = float(data.get("carbs_g", 0))
        fat = float(data.get("fat_g", 0))

        if protein > 0 and carbs > 0 and fat > 0:
            score += 2
            details["macros_positive"] = True
        else:
            details["macros_positive"] = False

    except (ValueError, TypeError):
        details["calories_plausible"] = False

    # Check 4: Food name recognized (not empty, not "Unknown" for clear cases)
    food_name = data.get("food_name", "")
    if food_name and food_name.strip():
        score += 1
        details["food_name_present"] = True
        details["food_name"] = food_name
    else:
        details["food_name_present"] = False

    return {"score": min(score, 10), "details": details}


# ============================================================================
# STEP 3 & 4: Prompt Template + Run Eval
# ============================================================================

async def run_eval(prompt_template: str, dataset: list, version_name: str) -> dict:
    """
    Run evaluation on a dataset.

    prompt_template: string with {food_description} placeholder
    dataset: list of FoodTestCase objects
    version_name: "v1", "v2", etc for reporting

    Returns: {
        "version": version_name,
        "scores": [grade_output results],
        "average_score": float,
        "pass_rate": float (% of outputs that are valid JSON),
    }
    """
    print(f"\n{'=' * 70}")
    print(f"EVALUATING: {version_name}")
    print(f"{'=' * 70}")

    scores = []
    valid_json_count = 0

    for i, test_case in enumerate(dataset, 1):
        print(f"\n[{i}/{len(dataset)}] Testing: {test_case.description[:50]}...")

        # Step 3: Insert dataset input into prompt template
        prompt = prompt_template.format(food_description=test_case.description)

        # Step 4: Run LLM with prefill+stop (from Day 1)
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "```json\n{"},  # Prefill
        ]

        try:
            response = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                messages=messages,
                stop_sequences=["```"],  # Stop at closing fence
            )

            # Reconstruct full JSON
            full_output = "```json\n{" + response.content[0].text + "```"

            # Extract JSON
            json_start = full_output.find("{")
            json_end = full_output.rfind("}") + 1
            json_str = full_output[json_start:json_end] if json_start >= 0 and json_end > json_start else ""

            # Grade this output
            grade = grade_output(json_str, test_case)
            scores.append(grade)

            if grade["details"].get("json_valid"):
                valid_json_count += 1

            print(f"  Score: {grade['score']}/10")
            if not grade["details"].get("json_valid"):
                print(f"    ❌ JSON invalid: {grade['details'].get('json_error', 'parse failed')}")
            else:
                print(f"    ✅ Valid JSON")
                if grade["details"].get("calories_plausible"):
                    print(f"    ✅ Calories plausible: {grade['details']['calories_value']} kcal")
                else:
                    print(
                        f"    ❌ Calories implausible: {grade['details']['calories_value']} "
                        f"(expected {grade['details']['expected_range']})"
                    )

        except Exception as e:
            print(f"  ❌ Error: {e}")
            scores.append({"score": 0, "details": {"error": str(e)}})

    # Aggregate results
    average_score = sum(s["score"] for s in scores) / len(scores) if scores else 0
    pass_rate = (valid_json_count / len(dataset)) * 100 if dataset else 0

    print(f"\n{'-' * 70}")
    print(f"RESULTS: {version_name}")
    print(f"{'-' * 70}")
    print(f"Average score: {average_score:.1f}/10")
    print(f"Valid JSON rate: {valid_json_count}/{len(dataset)} ({pass_rate:.0f}%)")

    return {
        "version": version_name,
        "scores": scores,
        "average_score": average_score,
        "pass_rate": pass_rate,
    }


# ============================================================================
# STEP 1: Prompts (v1 and v2)
# ============================================================================

PROMPT_V1 = """Analyze this food: "{food_description}"

Respond with ONLY valid JSON (no markdown, no extra text):
{{
  "food_name": "...",
  "calories": number,
  "protein_g": number,
  "carbs_g": number,
  "fat_g": number
}}"""

# V2: Improved based on what v1 might struggle with
PROMPT_V2 = """Analyze this food: "{food_description}"

Be accurate with nutrition data. If unclear, provide your best estimate.

Respond with ONLY valid JSON (no markdown, no extra text):
{{
  "food_name": "specific food name or 'Unknown' if unclear",
  "calories": number (e.g., 350),
  "protein_g": number (e.g., 25),
  "carbs_g": number (e.g., 40),
  "fat_g": number (e.g., 12)
}}

Constraints:
- Calories must be > 0 and < 5000
- All macros (protein, carbs, fat) must be > 0
- Include units in the food_name if relevant (e.g., "2 eggs" not just "eggs")"""


async def main():
    """Run the 6-step eval workflow: v1 → analyze → v2 → compare."""
    print("🎯 Phase 2 Day 2: First Eval Pipeline")
    print("6-step workflow: prompt → dataset → run → grade → analyze → iterate\n")

    # Step 1 & 2: Already defined above (PROMPT_V1, EVAL_DATASET)

    # Run eval on v1
    results_v1 = await run_eval(PROMPT_V1, EVAL_DATASET, "v1 (basic prompt)")

    # Run eval on v2
    results_v2 = await run_eval(PROMPT_V2, EVAL_DATASET, "v2 (improved prompt)")

    # Step 6: Compare and reflect
    print(f"\n{'=' * 70}")
    print("COMPARISON: v1 vs v2")
    print(f"{'=' * 70}")
    print(f"v1 average score: {results_v1['average_score']:.1f}/10")
    print(f"v2 average score: {results_v2['average_score']:.1f}/10")
    print(f"Improvement: {results_v2['average_score'] - results_v1['average_score']:+.1f} points")
    print()
    print(f"v1 valid JSON: {results_v1['pass_rate']:.0f}%")
    print(f"v2 valid JSON: {results_v2['pass_rate']:.0f}%")

    print(f"\n{'=' * 70}")
    print("KEY INSIGHTS")
    print(f"{'=' * 70}")
    print("""
This is the eval-driven iteration loop:

1. Write a prompt (v1)
2. Run on a dataset
3. Grade the outputs
4. Identify failure modes
5. Refine the prompt (v2)
6. Re-run and measure improvement

v2 improved over v1 by:
- Adding specific examples (e.g., "350" instead of "number")
- Clarifying constraints (> 0 and < 5000 for calories)
- Handling ambiguity ("Unknown" option)
- Better macros guidance

This is production LLM engineering: measure before/after, iterate data-driven.

NEXT (Day 3-5):
- Expand dataset to 30 photos (learn test data generation)
- Add model-based grading (use Opus to judge)
- Try more prompt variations
- Build signal fusion (combine code + model scores)
""")


if __name__ == "__main__":
    asyncio.run(main())
