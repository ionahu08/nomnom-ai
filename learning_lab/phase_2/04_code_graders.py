#!/usr/bin/env python3
"""
Phase 2 Day 4: Code-Based Grading

Build sophisticated graders that validate LLM output without needing another LLM.

Three grading techniques:
1. JSON validation — does it parse?
2. Schema validation — are required fields present and correct type?
3. Semantic validation — do the numeric values make sense nutritionally?

This script loads your generated dataset (Day 3) and runs it through your
prompts (Day 2), grading each output with code-based checks.

Usage:
    python 04_code_graders.py

This teaches you the foundation of eval infrastructure: automated scoring
without needing to call Opus/Claude as judge.
"""

import os
import json
import asyncio
from pathlib import Path
from anthropic import AsyncAnthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


# ============================================================================
# CODE-BASED GRADERS (No LLM needed)
# ============================================================================

class NutritionGrader:
    """Multi-level grading: JSON → schema → semantic."""

    def __init__(self):
        self.required_fields = {"food_name", "calories", "protein_g", "carbs_g", "fat_g"}

    def grade(self, output_str: str) -> dict:
        """
        Grade a nutrition JSON output.

        Returns: {
            "score": 0-100,
            "levels": {
                "json_valid": bool,
                "schema_valid": bool,
                "semantic_valid": bool,
            },
            "details": {...breakdown of each check...}
        }
        """
        details = {}
        levels = {}
        score = 0

        # LEVEL 1: JSON Validity
        levels["json_valid"] = self._check_json_valid(output_str, details)
        if not levels["json_valid"]:
            return {
                "score": 0,
                "levels": levels,
                "details": details,
                "reason": "JSON parsing failed",
            }
        score += 25  # 25 points for valid JSON

        # Parse JSON for further checks
        try:
            data = json.loads(output_str)
        except json.JSONDecodeError:
            return {
                "score": score,
                "levels": levels,
                "details": details,
                "reason": "Parsed JSON but failed to extract",
            }

        # LEVEL 2: Schema Validity
        levels["schema_valid"] = self._check_schema_valid(data, details)
        if not levels["schema_valid"]:
            return {
                "score": score,
                "levels": levels,
                "details": details,
                "reason": "Schema check failed (missing fields or wrong types)",
            }
        score += 25  # 25 points for valid schema

        # LEVEL 3: Semantic Validity (nutrition makes sense)
        levels["semantic_valid"] = self._check_semantic_valid(data, details)
        if levels["semantic_valid"]:
            score += 50  # 50 points for semantically valid nutrition
        else:
            score += 25  # Partial credit if some checks pass

        return {
            "score": score,
            "levels": levels,
            "details": details,
            "reason": "Grading complete",
        }

    def _check_json_valid(self, output_str: str, details: dict) -> bool:
        """LEVEL 1: Can we parse the output as JSON?"""
        try:
            json.loads(output_str)
            details["json_error"] = None
            return True
        except json.JSONDecodeError as e:
            details["json_error"] = str(e)
            return False

    def _check_schema_valid(self, data: dict, details: dict) -> bool:
        """LEVEL 2: Does the JSON have the right structure?"""
        # Check required fields exist
        missing = self.required_fields - set(data.keys())
        if missing:
            details["missing_fields"] = list(missing)
            return False

        # Check field types
        type_errors = []
        if not isinstance(data.get("food_name"), str) or not data["food_name"].strip():
            type_errors.append("food_name must be non-empty string")

        for field in ["calories", "protein_g", "carbs_g", "fat_g"]:
            try:
                float(data[field])
            except (ValueError, TypeError):
                type_errors.append(f"{field} must be numeric")

        if type_errors:
            details["type_errors"] = type_errors
            return False

        details["all_fields_present"] = True
        details["all_types_correct"] = True
        return True

    def _check_semantic_valid(self, data: dict, details: dict) -> bool:
        """LEVEL 3: Do the nutrition values make sense?"""
        checks = {}

        try:
            calories = float(data["calories"])
            protein = float(data["protein_g"])
            carbs = float(data["carbs_g"])
            fat = float(data["fat_g"])

            # Check 1: Calories in realistic range
            if 0 < calories < 5000:
                checks["calories_in_range"] = True
            else:
                checks["calories_in_range"] = False
                checks["calories_value"] = calories

            # Check 2: All macros positive
            if protein > 0 and carbs > 0 and fat > 0:
                checks["macros_positive"] = True
            else:
                checks["macros_positive"] = False
                checks["macro_values"] = {
                    "protein_g": protein,
                    "carbs_g": carbs,
                    "fat_g": fat,
                }

            # Check 3: Macro calories add up roughly to total
            # 1g protein = 4 cal, 1g carbs = 4 cal, 1g fat = 9 cal
            calculated_cal = (protein * 4) + (carbs * 4) + (fat * 9)
            calorie_diff = abs(calculated_cal - calories)

            # Allow 30% margin (macros may not account for all calories)
            margin = max(50, calories * 0.3)
            if calorie_diff < margin:
                checks["macro_calorie_consistency"] = True
            else:
                checks["macro_calorie_consistency"] = False
                checks["calculated_calories"] = calculated_cal
                checks["stated_calories"] = calories
                checks["difference"] = calorie_diff

            # Check 4: Reasonable portion size (not obviously wrong)
            # Most foods: 100-1000 kcal per serving
            if 100 <= calories <= 1000:
                checks["portion_reasonable"] = True
            else:
                checks["portion_reasonable"] = False
                checks["note"] = (
                    f"Unusual: {calories} kcal (typical range 100-1000). "
                    f"May be correct (e.g., large meal) or error."
                )

            details["semantic_checks"] = checks

            # All checks must pass for semantic validity
            all_pass = all(
                v
                for k, v in checks.items()
                if k not in ["calculated_calories", "stated_calories", "difference", "note", "macro_values", "calories_value"]
            )
            return all_pass

        except (ValueError, TypeError) as e:
            details["semantic_error"] = str(e)
            return False


# ============================================================================
# LOAD DATASET & RUN EVAL
# ============================================================================

def load_generated_dataset(filename: str = "generated_dataset.json") -> list:
    """Load the dataset generated on Day 3."""
    filepath = Path(f"learning_lab/phase_2/{filename}")

    if not filepath.exists():
        print(f"❌ Dataset not found at {filepath}")
        print(f"   Run 03_dataset_generation.py first")
        return []

    with open(filepath) as f:
        data = json.load(f)

    test_cases = data.get("test_cases", [])
    print(f"✅ Loaded {len(test_cases)} test cases from {filename}")
    return test_cases


# ============================================================================
# PROMPT & API CALL (reuse from Day 2)
# ============================================================================

PROMPT_TEMPLATE = """Analyze this food: "{food_description}"

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


async def call_claude(food_description: str) -> str:
    """Call Claude with prefill+stop (Day 1 technique)."""
    prompt = PROMPT_TEMPLATE.format(food_description=food_description)

    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "```json\n{"},  # Prefill
    ]

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=messages,
        stop_sequences=["```"],
    )

    # Reconstruct JSON
    full_output = "```json\n{" + response.content[0].text + "```"

    # Extract JSON
    json_start = full_output.find("{")
    json_end = full_output.rfind("}") + 1
    json_str = full_output[json_start:json_end] if json_start >= 0 and json_end > json_start else ""

    return json_str


async def run_full_eval(test_cases: list, sample_size: int = 10) -> dict:
    """
    Run evaluation on test cases.

    Args:
        test_cases: list of {"description": "..."}
        sample_size: only eval first N cases to save API calls

    Returns:
        {"results": [...], "stats": {...}}
    """
    grader = NutritionGrader()
    results = []

    print(f"\n{'=' * 70}")
    print(f"EVALUATING: {sample_size} test cases with code-based grader")
    print(f"{'=' * 70}\n")

    for i, test_case in enumerate(test_cases[:sample_size], 1):
        description = test_case.get("description", "")
        print(f"[{i}/{sample_size}] {description[:60]}...", end=" ")

        try:
            # Call Claude
            json_output = await call_claude(description)

            # Grade the output
            grade = grader.grade(json_output)

            results.append(
                {
                    "description": description,
                    "score": grade["score"],
                    "levels": grade["levels"],
                    "details": grade["details"],
                }
            )

            # Print inline result
            if grade["levels"]["json_valid"] and grade["levels"]["schema_valid"]:
                print(f"✅ Score: {grade['score']}/100")
            else:
                print(f"❌ Score: {grade['score']}/100 ({grade['reason']})")

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(
                {
                    "description": description,
                    "score": 0,
                    "error": str(e),
                }
            )

    # Compute statistics
    scores = [r["score"] for r in results if "score" in r]
    avg_score = sum(scores) / len(scores) if scores else 0
    valid_json = sum(
        1 for r in results if r.get("levels", {}).get("json_valid", False)
    )
    valid_schema = sum(
        1 for r in results if r.get("levels", {}).get("schema_valid", False)
    )

    return {
        "results": results,
        "stats": {
            "total_cases": len(results),
            "average_score": avg_score,
            "valid_json_count": valid_json,
            "valid_schema_count": valid_schema,
            "valid_json_pct": (valid_json / len(results) * 100) if results else 0,
            "valid_schema_pct": (valid_schema / len(results) * 100) if results else 0,
        },
    }


async def main():
    """Load dataset, run eval, show results."""
    print("🎯 Phase 2 Day 4: Code-Based Grading")
    print("Build graders that validate LLM output without needing another LLM\n")

    # Load dataset from Day 3
    test_cases = load_generated_dataset()
    if not test_cases:
        return

    # Run eval on all 30 cases
    eval_result = await run_full_eval(test_cases, sample_size=30)

    # Show results
    print(f"\n{'=' * 70}")
    print("GRADING RESULTS")
    print(f"{'=' * 70}\n")

    stats = eval_result["stats"]
    print(f"Average score: {stats['average_score']:.1f}/100")
    print(f"Valid JSON: {stats['valid_json_count']}/{stats['total_cases']} ({stats['valid_json_pct']:.0f}%)")
    print(f"Valid schema: {stats['valid_schema_count']}/{stats['total_cases']} ({stats['valid_schema_pct']:.0f}%)")

    print(f"\n{'=' * 70}")
    print("GRADING LEVELS EXPLAINED")
    print(f"{'=' * 70}")
    print("""
Level 1: JSON Validity (25 points)
  - Can Python parse it as JSON?
  - If this fails, downstream checks don't run

Level 2: Schema Validity (25 points)
  - Are all required fields present?
  - Are fields the correct type? (food_name is string, calories is number)
  - If this fails, semantic checks are unreliable

Level 3: Semantic Validity (50 points)
  - Calories in realistic range (0-5000)?
  - All macros positive (protein, carbs, fat > 0)?
  - Do macros + calories align mathematically? (protein*4 + carbs*4 + fat*9 ≈ calories)
  - Portion size reasonable (100-1000 kcal)?

Max score: 100 (all levels pass)

WHY THIS MATTERS:
- Code-based grading is deterministic (no randomness like LLM-as-judge)
- Fast and cheap (no API calls for grading)
- Catches structural errors (missing fields, type mismatches)
- Catches semantic errors (impossible nutrition values)

NEXT (Day 5):
- Add model-based grading (use Opus to evaluate quality)
- Combine code + model scores (signal fusion, RecSys-style)
- Compare code-only vs. hybrid grading
""")

    print(f"\n{'=' * 70}")
    print("SAMPLE DETAILED RESULTS")
    print(f"{'=' * 70}\n")

    for result in eval_result["results"][:5]:
        print(f"Food: {result['description'][:60]}...")
        print(f"Score: {result['score']}/100")
        if "levels" in result:
            levels = result["levels"]
            print(
                f"  JSON: {'✅' if levels.get('json_valid') else '❌'} | "
                f"Schema: {'✅' if levels.get('schema_valid') else '❌'} | "
                f"Semantic: {'✅' if levels.get('semantic_valid') else '❌'}"
            )
        print()


if __name__ == "__main__":
    asyncio.run(main())
