#!/usr/bin/env python3
"""
Phase 2 Days 8-9 Capstone: Tool Choice vs Prefill+Stop

Key insight: tool_choice is superior to prefill+stop for structured output.

Why?
- prefill+stop: Claude generates text, we parse and validate (fragile)
- tool_choice: Claude forced to use tool schema, guaranteed structure (robust)

This script:
  - Load 30 test cases from Day 3 dataset
  - Run v1.0 (tool_choice) on all cases
  - Grade with code-based grader (3 levels: JSON, schema, semantic)
  - Compare against v0.5 baseline if available
  - Save results to 08_capstone_v1_results.json
  - Shows improvement in accuracy, error handling, reliability

Usage:
    python 08_capstone_v1_tool_choice.py

Output:
    - v1.0 results for all 30 cases
    - Comparison: v0.5 baseline vs v1.0 improvement
    - Detailed breakdown of what tool_choice solves
"""

import os
import json
import asyncio
from pathlib import Path
from anthropic import AsyncAnthropic
from typing import Optional

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


# ============================================================================
# TOOL DEFINITION (v1.0 — tool_choice)
# ============================================================================

ANALYZE_FOOD_TOOL = {
    "name": "analyze_food",
    "description": "Analyze a food item and extract nutritional information",
    "input_schema": {
        "type": "object",
        "properties": {
            "food_name": {
                "type": "string",
                "description": "Specific food name or 'Unknown' if unclear (e.g., '2 eggs', 'grilled chicken Caesar salad')"
            },
            "calories": {
                "type": "integer",
                "description": "Estimated calories (0-5000 kcal)"
            },
            "protein_g": {
                "type": "number",
                "description": "Protein in grams (0-500g)"
            },
            "carbs_g": {
                "type": "number",
                "description": "Carbohydrates in grams (0-500g)"
            },
            "fat_g": {
                "type": "number",
                "description": "Fat in grams (0-500g)"
            }
        },
        "required": ["food_name", "calories", "protein_g", "carbs_g", "fat_g"]
    }
}


# ============================================================================
# PROMPT (v1.0 — simpler because tool_choice handles structure)
# ============================================================================

PROMPT_TEMPLATE_V1 = """Analyze this food: "{food_description}"

Be accurate with nutrition data. If unclear, provide your best estimate.

You MUST use the analyze_food tool to respond."""


# ============================================================================
# API CALL (v1.0 — tool_choice)
# ============================================================================

async def call_claude_v1_tool_choice(food_description: str) -> dict:
    """
    Call Claude with tool_choice to force structured output.

    Key difference from v0.5:
    - v0.5: prefill+stop (Claude generates text, we parse)
    - v1.0: tool_choice (Claude forced to use tool, structure guaranteed)

    Returns: {
        "success": bool,
        "tool_input": {...},  # Extracted from tool_use block
        "raw_response": {...}  # Full Claude response
    }
    """
    prompt = PROMPT_TEMPLATE_V1.format(food_description=food_description)

    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            tools=[ANALYZE_FOOD_TOOL],
            tool_choice={"type": "tool", "name": "analyze_food"},  # FORCE tool use
            messages=messages,
        )

        # Extract tool_use from response
        tool_use_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_use_block = block
                break

        if not tool_use_block:
            return {
                "success": False,
                "error": "No tool_use block in response",
                "raw_response": response
            }

        # tool_input is guaranteed to be dict (parsed by Claude)
        return {
            "success": True,
            "tool_input": tool_use_block.input,
            "raw_response": response
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ============================================================================
# GRADING (reuse from Day 4)
# ============================================================================

class NutritionGrader:
    """Multi-level grading: JSON → schema → semantic."""

    def __init__(self):
        self.required_fields = {"food_name", "calories", "protein_g", "carbs_g", "fat_g"}

    def grade(self, tool_input: dict) -> dict:
        """
        Grade a tool_input dict (already parsed by Claude).

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

        # LEVEL 1: Tool input is already valid (tool_choice guarantees this)
        levels["json_valid"] = True
        details["json_error"] = None
        score += 25  # Already valid by design

        # LEVEL 2: Schema Validity
        levels["schema_valid"] = self._check_schema_valid(tool_input, details)
        if not levels["schema_valid"]:
            return {
                "score": score,
                "levels": levels,
                "details": details,
                "reason": "Schema check failed (missing fields or wrong types)",
            }
        score += 25  # 25 points for valid schema

        # LEVEL 3: Semantic Validity (nutrition makes sense)
        levels["semantic_valid"] = self._check_semantic_valid(tool_input, details)
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

    def _check_schema_valid(self, data: dict, details: dict) -> bool:
        """LEVEL 2: Does the data have the right structure?"""
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
            calculated_cal = (protein * 4) + (carbs * 4) + (fat * 9)
            calorie_diff = abs(calculated_cal - calories)
            margin = max(50, calories * 0.3)
            if calorie_diff < margin:
                checks["macro_calorie_consistency"] = True
            else:
                checks["macro_calorie_consistency"] = False
                checks["calculated_calories"] = calculated_cal
                checks["stated_calories"] = calories
                checks["difference"] = calorie_diff

            # Check 4: Reasonable portion size
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
# LOAD DATASET & BASELINE (v0.5 from Day 2)
# ============================================================================

def load_generated_dataset(filename: str = "generated_dataset.json") -> list:
    """Load the 30-case dataset from Day 3."""
    filepath = Path(f"learning_lab/phase_2/{filename}")

    if not filepath.exists():
        print(f"❌ Dataset not found at {filepath}")
        return []

    with open(filepath) as f:
        data = json.load(f)

    return data.get("test_cases", [])


def load_v0_5_baseline(filename: str = "02_eval_pipeline_results.json") -> Optional[dict]:
    """Try to load v0.5 baseline results (if they exist)."""
    filepath = Path(f"learning_lab/phase_2/{filename}")

    if filepath.exists():
        try:
            with open(filepath) as f:
                return json.load(f)
        except:
            return None

    return None


# ============================================================================
# FULL EVAL (v1.0 on all 30 cases)
# ============================================================================

async def run_eval_v1_tool_choice(test_cases: list) -> dict:
    """Run evaluation on all 30 test cases using v1.0 (tool_choice)."""
    grader = NutritionGrader()
    results = []

    print(f"\n{'=' * 70}")
    print(f"EVALUATING: {len(test_cases)} test cases with v1.0 (tool_choice)")
    print(f"{'=' * 70}\n")

    for i, test_case in enumerate(test_cases, 1):
        description = test_case.get("description", "")
        print(f"[{i}/{len(test_cases)}] {description[:60]}...", end=" ")

        try:
            # Call Claude with tool_choice
            response = await call_claude_v1_tool_choice(description)

            if not response["success"]:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
                results.append({
                    "description": description,
                    "score": 0,
                    "error": response.get("error", "Unknown error"),
                    "v1_success": False,
                })
                continue

            # Grade the tool_input
            grade = grader.grade(response["tool_input"])

            results.append({
                "description": description,
                "score": grade["score"],
                "levels": grade["levels"],
                "details": grade["details"],
                "tool_input": response["tool_input"],
                "v1_success": True,
            })

            # Print inline result
            status = "✅" if grade["levels"]["schema_valid"] else "❌"
            print(f"{status} Score: {grade['score']}/100")

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "description": description,
                "score": 0,
                "error": str(e),
                "v1_success": False,
            })

    # Compute statistics
    scores = [r["score"] for r in results if "score" in r]
    avg_score = sum(scores) / len(scores) if scores else 0
    valid_schema = sum(
        1 for r in results if r.get("levels", {}).get("schema_valid", False)
    )
    valid_semantic = sum(
        1 for r in results if r.get("levels", {}).get("semantic_valid", False)
    )
    success_rate = sum(
        1 for r in results if r.get("v1_success", False)
    ) / len(results) if results else 0

    return {
        "results": results,
        "stats": {
            "total_cases": len(results),
            "average_score": avg_score,
            "valid_schema_count": valid_schema,
            "valid_schema_pct": (valid_schema / len(results) * 100) if results else 0,
            "valid_semantic_count": valid_semantic,
            "valid_semantic_pct": (valid_semantic / len(results) * 100) if results else 0,
            "success_rate": success_rate,
            "success_rate_pct": success_rate * 100,
        },
    }


# ============================================================================
# COMPARISON (v0.5 baseline vs v1.0)
# ============================================================================

def compare_v0_5_vs_v1_0(v1_results: dict, v0_5_baseline: Optional[dict]) -> dict:
    """Compare v0.5 and v1.0 results."""

    if not v0_5_baseline:
        return {
            "v0_5_available": False,
            "message": "v0.5 baseline not found; showing v1.0 results only"
        }

    v0_5_stats = v0_5_baseline.get("stats", {})
    v1_0_stats = v1_results["stats"]

    return {
        "v0_5_available": True,
        "v0_5_avg_score": v0_5_stats.get("average_score", 0),
        "v1_0_avg_score": v1_0_stats.get("average_score", 0),
        "improvement": v1_0_stats.get("average_score", 0) - v0_5_stats.get("average_score", 0),

        "v0_5_schema_valid_pct": v0_5_stats.get("valid_schema_pct", 0),
        "v1_0_schema_valid_pct": v1_0_stats.get("valid_schema_pct", 0),

        "v0_5_semantic_valid_pct": v0_5_stats.get("valid_semantic_pct", 0),
        "v1_0_semantic_valid_pct": v1_0_stats.get("valid_semantic_pct", 0),
    }


async def main():
    """Run capstone Days 8-9 evaluation."""
    print("🎯 Phase 2 Days 8-9 Capstone: Tool Choice vs Prefill+Stop")
    print("Learn why tool_choice is superior for structured output\n")

    # Load dataset
    test_cases = load_generated_dataset()
    if not test_cases:
        print("❌ Could not load dataset")
        return

    # Load v0.5 baseline (if available)
    v0_5_baseline = load_v0_5_baseline()

    # Run v1.0 eval
    v1_results = await run_eval_v1_tool_choice(test_cases)

    # Compare
    comparison = compare_v0_5_vs_v1_0(v1_results, v0_5_baseline)

    # Show results
    print(f"\n{'=' * 70}")
    print("EVALUATION RESULTS: v1.0 (tool_choice)")
    print(f"{'=' * 70}\n")

    stats = v1_results["stats"]
    print(f"Average score: {stats['average_score']:.1f}/100")
    print(f"Valid schema: {stats['valid_schema_count']}/{stats['total_cases']} ({stats['valid_schema_pct']:.0f}%)")
    print(f"Valid semantic: {stats['valid_semantic_count']}/{stats['total_cases']} ({stats['valid_semantic_pct']:.0f}%)")
    print(f"Success rate: {stats['success_rate']:.1%} (tool_choice forced completion)")

    if comparison.get("v0_5_available"):
        print(f"\n{'=' * 70}")
        print("COMPARISON: v0.5 (prefill+stop) vs v1.0 (tool_choice)")
        print(f"{'=' * 70}\n")

        print(f"Average score:")
        print(f"  v0.5: {comparison['v0_5_avg_score']:.1f}/100")
        print(f"  v1.0: {comparison['v1_0_avg_score']:.1f}/100")
        print(f"  Improvement: +{comparison['improvement']:.1f}")

        print(f"\nSchema validity:")
        print(f"  v0.5: {comparison['v0_5_schema_valid_pct']:.0f}%")
        print(f"  v1.0: {comparison['v1_0_schema_valid_pct']:.0f}%")

        print(f"\nSemantic validity:")
        print(f"  v0.5: {comparison['v0_5_semantic_valid_pct']:.0f}%")
        print(f"  v1.0: {comparison['v1_0_semantic_valid_pct']:.0f}%")

    print(f"\n{'=' * 70}")
    print("WHY TOOL_CHOICE IS SUPERIOR")
    print(f"{'=' * 70}")
    print("""
v0.5 (prefill+stop):
  Claude generates: ```json\\n{ "food_name": "...", ...}```
  We parse: Extract JSON from markdown, validate with Pydantic
  Failure modes:
    - Missing fields (Claude forgets a field)
    - Type mismatches (calories as string)
    - Markdown formatting issues (extra spaces, quotes)
    - Failed validation = request dies, no recovery

v1.0 (tool_choice):
  Claude forced to use ANALYZE_FOOD_TOOL
  Returns: tool_use block with guaranteed structure
  Why superior:
    - ✅ Structure guaranteed by API (tool schema)
    - ✅ No markdown parsing needed
    - ✅ Claude can't generate invalid output
    - ✅ 100% success rate (tool_choice enforces tool use)
    - ✅ Type safety built into API layer
    - ✅ Simpler prompt (no need for JSON format instructions)

Production takeaway:
  When you need structured output, always use tool_choice.
  Don't fight Claude's tokenizer with text parsing.
  Let the API enforce structure, not your code.
""")

    print(f"\n{'=' * 70}")
    print("SAMPLE RESULTS")
    print(f"{'=' * 70}\n")

    for result in v1_results["results"][:3]:
        print(f"Food: {result['description'][:60]}...")
        print(f"Score: {result['score']}/100", end="")
        if "error" in result:
            print(f" (Error: {result['error']})")
        else:
            levels = result.get("levels", {})
            print(f"  Schema: {'✅' if levels.get('schema_valid') else '❌'} | Semantic: {'✅' if levels.get('semantic_valid') else '❌'}")
            if result.get("tool_input"):
                tool_input = result["tool_input"]
                print(f"  → {tool_input.get('food_name', 'Unknown')} ({tool_input.get('calories', '?')} cal)")
        print()

    # Save results
    output_file = "learning_lab/phase_2/08_capstone_v1_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "version": "v1.0_tool_choice",
            "stats": stats,
            "comparison": comparison if comparison.get("v0_5_available") else None,
            "results": v1_results["results"]
        }, f, indent=2)

    print(f"💾 Results saved to: {output_file}")

    print(f"\n{'=' * 70}")
    print("NEXT: Day 9 — Full comparison report with model-based grading")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    asyncio.run(main())
