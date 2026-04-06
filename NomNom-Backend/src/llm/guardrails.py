"""
Guardrails — Validate AI output to catch hallucinations and safety issues.

In Plain English:
LLMs can hallucinate. This module checks AI output is sensible:
- Calories aren't 500,000
- Food name isn't empty or gibberish
- Roast isn't hateful or toxic
- Nutritional values are in reasonable ranges

If anything fails a guard, we log it and either fix it or reject it.
"""

import logging
from typing import Optional

from src.schemas.food_log import FoodAnalysisResponse

logger = logging.getLogger(__name__)


class GuardrailViolation(Exception):
    """Raised when AI output violates a guardrail."""

    pass


class FoodAnalysisGuardrails:
    """Guardrails for food analysis responses."""

    # Safe ranges
    CALORIE_MIN = 0
    CALORIE_MAX = 5000
    MACRO_MIN = 0
    MACRO_MAX = 500

    # String lengths
    FOOD_NAME_MIN_LEN = 1
    FOOD_NAME_MAX_LEN = 200
    ROAST_MIN_LEN = 1
    ROAST_MAX_LEN = 500

    # Forbidden phrases (basic toxicity check)
    FORBIDDEN_PHRASES = [
        "kill yourself",
        "kys",
        "hate you",
        "should die",
        "bomb",
        "terrorist",
    ]

    @staticmethod
    def validate(analysis: FoodAnalysisResponse) -> FoodAnalysisResponse:
        """
        Validate a food analysis response against guardrails.

        Args:
            analysis: FoodAnalysisResponse to validate

        Returns:
            Same response if all guards pass

        Raises:
            GuardrailViolation: If any guard fails
        """
        # Check calories
        if not (FoodAnalysisGuardrails.CALORIE_MIN <= analysis.calories <= FoodAnalysisGuardrails.CALORIE_MAX):
            raise GuardrailViolation(
                f"Calories {analysis.calories} out of range [{FoodAnalysisGuardrails.CALORIE_MIN}, {FoodAnalysisGuardrails.CALORIE_MAX}]"
            )

        # Check macros
        for macro_name, macro_value in [
            ("protein", analysis.protein_g),
            ("carbs", analysis.carbs_g),
            ("fat", analysis.fat_g),
        ]:
            if not (FoodAnalysisGuardrails.MACRO_MIN <= macro_value <= FoodAnalysisGuardrails.MACRO_MAX):
                raise GuardrailViolation(
                    f"{macro_name.title()} {macro_value}g out of range [{FoodAnalysisGuardrails.MACRO_MIN}, {FoodAnalysisGuardrails.MACRO_MAX}]"
                )

        # Check food name
        if not analysis.food_name or not analysis.food_name.strip():
            raise GuardrailViolation("Food name is empty")

        if not (
            FoodAnalysisGuardrails.FOOD_NAME_MIN_LEN
            <= len(analysis.food_name)
            <= FoodAnalysisGuardrails.FOOD_NAME_MAX_LEN
        ):
            raise GuardrailViolation(
                f"Food name length {len(analysis.food_name)} out of range [{FoodAnalysisGuardrails.FOOD_NAME_MIN_LEN}, {FoodAnalysisGuardrails.FOOD_NAME_MAX_LEN}]"
            )

        # Check roast
        if not analysis.cat_roast or not analysis.cat_roast.strip():
            raise GuardrailViolation("Cat roast is empty")

        if not (
            FoodAnalysisGuardrails.ROAST_MIN_LEN
            <= len(analysis.cat_roast)
            <= FoodAnalysisGuardrails.ROAST_MAX_LEN
        ):
            raise GuardrailViolation(
                f"Roast length {len(analysis.cat_roast)} out of range [{FoodAnalysisGuardrails.ROAST_MIN_LEN}, {FoodAnalysisGuardrails.ROAST_MAX_LEN}]"
            )

        # Check for toxic content in roast
        roast_lower = analysis.cat_roast.lower()
        for phrase in FoodAnalysisGuardrails.FORBIDDEN_PHRASES:
            if phrase in roast_lower:
                raise GuardrailViolation(
                    f"Roast contains forbidden phrase: '{phrase}'"
                )

        # Check calorie distribution (basic sanity check)
        # Max calories per macro: protein 4cal/g, carbs 4cal/g, fat 9cal/g
        # Allow 20% margin for rounding
        max_possible_calories = (analysis.protein_g * 4) + (analysis.carbs_g * 4) + (analysis.fat_g * 9)
        if analysis.calories > max_possible_calories * 1.2:
            logger.warning(
                f"Calorie distribution suspicious: {analysis.calories} cal but macros only add up to ~{max_possible_calories} cal"
            )
            # Don't fail hard, just warn — macros might be estimated separately

        logger.info(
            "Food analysis passed guardrails",
            extra={
                "food_name": analysis.food_name,
                "calories": analysis.calories,
            },
        )

        return analysis

    @staticmethod
    def get_violation_reason(error: GuardrailViolation) -> str:
        """Get human-readable reason for guardrail violation."""
        return str(error)
