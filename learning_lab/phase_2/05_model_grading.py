#!/usr/bin/env python3
"""
Phase 2 Day 5: Model-Based Grading (LLM-as-Judge)

Key insight: Don't just ask an LLM for a score. Ask for:
- Strengths: What did Claude get right?
- Weaknesses: What did Claude get wrong or miss?
- Reasoning: Why does this score make sense?
- Score: Overall quality (0-10)

This structured output teaches you *why* outputs fail, not just *that* they fail.

The pattern:
1. Haiku generates nutrition JSON (from your prompt)
2. Opus evaluates that JSON (as judge)
3. Opus returns structured critique
4. You combine: code_score + model_score = final_score

This teaches you signal fusion (RecSys pattern): combining multiple signals
into one decision.

Usage:
    python 05_model_grading.py

This evaluates all 30 test cases with model-based grading (expensive in API calls,
but gives you rich qualitative feedback).
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
# MODEL-BASED GRADER (uses Opus to evaluate)
# ============================================================================

GRADER_PROMPT = """You are an expert nutritionist and food analyst. Your job is to evaluate
whether Claude's food analysis is accurate and reasonable.

Food description: {food_description}

Claude's analysis:
{claude_output}

Evaluate this analysis on these dimensions:
1. Food identification: Is the identified food reasonable given the description?
2. Calorie estimate: Are the calories plausible for this food?
3. Macro estimates: Do protein/carbs/fat seem reasonable and consistent?
4. Completeness: Is all required info present?

Respond with ONLY valid JSON (no markdown):
{{
  "food_identification_quality": "excellent/good/fair/poor",
  "calorie_estimate_quality": "excellent/good/fair/poor",
  "macro_estimate_quality": "excellent/good/fair/poor",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "reasoning": "1-2 sentences explaining the score",
  "score": number (0-10, where 10 is excellent and 0 is completely wrong)
}}"""


async def grade_with_opus(food_description: str, claude_output: str) -> dict:
    """
    Use Opus (stronger model) to grade Haiku's output.

    Returns: {
        "score": 0-10,
        "strengths": [...],
        "weaknesses": [...],
        "reasoning": "...",
        "details": {...full response...}
    }
    """
    prompt = GRADER_PROMPT.format(
        food_description=food_description,
        claude_output=claude_output,
    )

    messages = [
        {"role": "user", "content": prompt},
    ]

    try:
        response = await client.messages.create(
            model="claude-opus-4-1-20250805",  # Use Opus for grading (more capable)
            max_tokens=500,
            messages=messages,
        )

        output_text = response.content[0].text

        # Try to parse JSON
        try:
            grade = json.loads(output_text)
            return {
                "score": grade.get("score", 5),
                "strengths": grade.get("strengths", []),
                "weaknesses": grade.get("weaknesses", []),
                "reasoning": grade.get("reasoning", ""),
                "details": grade,
            }
        except json.JSONDecodeError:
            # If JSON parse fails, try to extract JSON from response
            json_start = output_text.find("{")
            json_end = output_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = output_text[json_start:json_end]
                try:
                    grade = json.loads(json_str)
                    return {
                        "score": grade.get("score", 5),
                        "strengths": grade.get("strengths", []),
                        "weaknesses": grade.get("weaknesses", []),
                        "reasoning": grade.get("reasoning", ""),
                        "details": grade,
                    }
                except json.JSONDecodeError:
                    return {
                        "score": 0,
                        "error": "Opus returned invalid JSON",
                        "raw_output": output_text,
                    }

    except Exception as e:
        return {
            "score": 0,
            "error": str(e),
        }


# ============================================================================
# LOAD DATASET & GET HAIKU OUTPUTS
# ============================================================================

def load_generated_dataset(filename: str = "generated_dataset.json") -> list:
    """Load the dataset generated on Day 3."""
    filepath = Path(f"learning_lab/phase_2/{filename}")

    if not filepath.exists():
        print(f"❌ Dataset not found at {filepath}")
        return []

    with open(filepath) as f:
        data = json.load(f)

    return data.get("test_cases", [])


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


async def call_haiku(food_description: str) -> str:
    """Call Haiku to generate nutrition analysis."""
    prompt = PROMPT_TEMPLATE.format(food_description=food_description)

    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "```json\n{"},
    ]

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=messages,
        stop_sequences=["```"],
    )

    full_output = "```json\n{" + response.content[0].text + "```"
    json_start = full_output.find("{")
    json_end = full_output.rfind("}") + 1
    json_str = full_output[json_start:json_end] if json_start >= 0 and json_end > json_start else ""

    return json_str


# ============================================================================
# SIGNAL FUSION (RecSys pattern)
# ============================================================================

def combine_scores(code_score: int, model_score: int) -> dict:
    """
    Combine code-based score and model-based score.

    RecSys pattern: multiple signals → final decision

    Args:
        code_score: 0-100 from code grader
        model_score: 0-10 from model grader

    Returns:
        {"final_score": 0-100, "breakdown": {...}}
    """
    # Normalize model score to 0-100
    model_score_normalized = (model_score / 10) * 100

    # Weight: code structure is 40%, quality is 60%
    # (You might adjust these weights based on what matters more)
    final_score = (code_score * 0.4) + (model_score_normalized * 0.6)

    return {
        "final_score": final_score,
        "code_score": code_score,
        "model_score": model_score,
        "model_score_normalized": model_score_normalized,
        "weights": {"code": 0.4, "model": 0.6},
    }


# ============================================================================
# FULL EVAL WITH BOTH GRADERS
# ============================================================================

async def run_full_eval_with_model_grading(test_cases: list, sample_size: int = 10) -> dict:
    """
    Run evaluation with both code and model graders.

    This is expensive (Opus calls for each case), so default to 10.
    """
    results = []

    print(f"\n{'=' * 70}")
    print(f"EVALUATING: {sample_size} test cases with code + model grading")
    print(f"(This uses Opus for quality judgment — expensive but rich feedback)")
    print(f"{'=' * 70}\n")

    for i, test_case in enumerate(test_cases[:sample_size], 1):
        description = test_case.get("description", "")
        print(f"[{i}/{sample_size}] {description[:50]}...")

        try:
            # Step 1: Get Haiku's output
            haiku_output = await call_haiku(description)

            # Step 2: Code-based grade (simplified version)
            # For brevity, we'll give it a simple score based on JSON validity
            code_score = 100 if haiku_output and "{" in haiku_output else 0

            # Step 3: Model-based grade (Opus evaluates)
            model_grade = await grade_with_opus(description, haiku_output)

            # Step 4: Combine scores
            combined = combine_scores(code_score, model_grade.get("score", 5))

            results.append(
                {
                    "description": description,
                    "haiku_output": haiku_output,
                    "code_score": code_score,
                    "model_grade": model_grade,
                    "combined_score": combined,
                }
            )

            print(
                f"  Code: {code_score}/100 | "
                f"Model: {model_grade.get('score', 0)}/10 | "
                f"Final: {combined['final_score']:.1f}/100"
            )

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(
                {
                    "description": description,
                    "error": str(e),
                }
            )

    # Aggregate statistics
    valid_results = [r for r in results if "error" not in r]
    if valid_results:
        avg_final = sum(r["combined_score"]["final_score"] for r in valid_results) / len(
            valid_results
        )
        avg_model = sum(r["model_grade"].get("score", 0) for r in valid_results) / len(
            valid_results
        )
    else:
        avg_final = 0
        avg_model = 0

    return {
        "results": results,
        "stats": {
            "total_cases": len(results),
            "avg_final_score": avg_final,
            "avg_model_score": avg_model,
        },
    }


async def main():
    """Run full eval with code + model grading."""
    print("🎯 Phase 2 Day 5: Model-Based Grading (LLM-as-Judge)")
    print("Learn signal fusion: combine code + model scores for rich feedback\n")

    # Load dataset
    test_cases = load_generated_dataset()
    if not test_cases:
        return

    # Run eval (sample_size=10 to save API costs; increase if desired)
    eval_result = await run_full_eval_with_model_grading(test_cases, sample_size=10)

    # Show results
    print(f"\n{'=' * 70}")
    print("GRADING RESULTS: Code + Model")
    print(f"{'=' * 70}\n")

    stats = eval_result["stats"]
    print(f"Average final score (combined): {stats['avg_final_score']:.1f}/100")
    print(f"Average model score: {stats['avg_model_score']:.1f}/10")

    print(f"\n{'=' * 70}")
    print("SIGNAL FUSION EXPLAINED")
    print(f"{'=' * 70}")
    print("""
RecSys Pattern: Multiple Signals → Final Decision

You now have two signals:
1. Code-based score (0-100): Structure, schema, semantics
   - Deterministic, fast, cheap
   - Catches structural errors
   - Misses quality judgments

2. Model-based score (0-10): Quality, accuracy, reasoning
   - Uses Opus (more capable judge)
   - Expensive, but rich qualitative feedback
   - Catches semantic/reasoning errors

Fusion: final_score = (code_score * 0.4) + (model_score_normalized * 0.6)
  - 40% weight on structure
  - 60% weight on quality
  - You can adjust weights based on priorities

This is identical to RecSys multi-channel scoring:
  - Channel 1: CTR (code structure)
  - Channel 2: LTV (model quality)
  - Final: weighted combination

Why both?
- Code is fast feedback on every call (cheap to run)
- Model is deep feedback on important cases (expensive, use sparingly)
- Combined: cheap structure checks + expensive quality checks on edge cases
""")

    print(f"\n{'=' * 70}")
    print("SAMPLE DETAILED RESULTS")
    print(f"{'=' * 70}\n")

    for result in eval_result["results"][:3]:
        if "error" in result:
            continue

        print(f"Food: {result['description'][:60]}...")
        print(f"Haiku output: {result['haiku_output'][:80]}...")
        print()
        print(f"Code score: {result['code_score']}/100")
        print(f"Model score: {result['model_grade'].get('score', 0)}/10")
        print(f"Final score: {result['combined_score']['final_score']:.1f}/100")
        print()

        if "strengths" in result["model_grade"]:
            strengths = result["model_grade"].get("strengths", [])
            print(f"Strengths:")
            for s in strengths[:2]:
                print(f"  • {s}")

            weaknesses = result["model_grade"].get("weaknesses", [])
            print(f"Weaknesses:")
            for w in weaknesses[:2]:
                print(f"  • {w}")

        print(f"Reasoning: {result['model_grade'].get('reasoning', 'N/A')}")
        print()

    print(f"\n{'=' * 70}")
    print("NEXT STEPS")
    print(f"{'=' * 70}")
    print("""
Day 5 complete. You now have:
✅ Code-based grading (Day 4) — structure validation
✅ Model-based grading (Day 5) — quality judgment
✅ Signal fusion — combined scoring

AFTERNOON (Day 5):
Read Anthropic Tool Use documentation to understand:
- Tool schemas (JSON Schema syntax)
- tool_choice parameter
- tool_use blocks in responses
- tool_result blocks in followup messages

This prepares you for Days 8-9 capstone where you'll use tool_choice
to force structured output (replacing prefill+stop).

NEXT WEEK (Days 6-10):
- Days 6-7: Code review of production parser.py + guardrails.py
- Days 8-9: Capstone — eval pipeline with tool_choice
- Day 10: Production refactor
""")


if __name__ == "__main__":
    asyncio.run(main())
