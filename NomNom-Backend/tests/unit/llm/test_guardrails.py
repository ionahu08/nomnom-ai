"""
Tests for guardrails — output validation.

Note: Pydantic already validates:
- Calorie range (0-5000)
- Macro ranges (0-500g each)
- Food name length (1-200 chars)
- Roast length (1-500 chars)

Guardrails focuses on things Pydantic doesn't check:
- Toxicity (forbidden phrases)
- Content safety
- Calorie distribution sanity check
"""

import pytest

from src.llm.guardrails import FoodAnalysisGuardrails, GuardrailViolation
from src.schemas.food_log import FoodAnalysisResponse


class TestValidAnalysis:
    """Test validation with valid data."""

    def test_valid_analysis(self):
        """Valid analysis should pass all guards."""
        analysis = FoodAnalysisResponse(
            food_name="Pizza",
            calories=500,
            protein_g=20,
            carbs_g=60,
            fat_g=20,
            food_category="fast food",
            cuisine_origin="Italian",
            cat_roast="Classic.",
        )
        result = FoodAnalysisGuardrails.validate(analysis)
        assert result.calories == 500

    def test_zero_calories(self):
        """Zero calories should be valid (water, empty plate)."""
        analysis = FoodAnalysisResponse(
            food_name="Water",
            calories=0,
            protein_g=0,
            carbs_g=0,
            fat_g=0,
            food_category="drink",
            cuisine_origin="universal",
            cat_roast="Boring.",
        )
        result = FoodAnalysisGuardrails.validate(analysis)
        assert result.calories == 0

    def test_max_values(self):
        """Max allowed values should pass."""
        analysis = FoodAnalysisResponse(
            food_name="A" * 200,  # Max food name length
            calories=5000,  # Max calories
            protein_g=500,  # Max protein
            carbs_g=500,  # Max carbs
            fat_g=500,  # Max fat
            food_category="feast",
            cuisine_origin="American",
            cat_roast="A" * 500,  # Max roast length
        )
        result = FoodAnalysisGuardrails.validate(analysis)
        assert result.calories == 5000
        assert len(result.food_name) == 200
        assert len(result.cat_roast) == 500


class TestToxicityGuardrails:
    """Test toxicity/safety checks."""

    def test_roast_with_forbidden_phrase(self):
        """Roast with forbidden phrase should fail."""
        analysis = FoodAnalysisResponse(
            food_name="Pizza",
            calories=500,
            protein_g=20,
            carbs_g=60,
            fat_g=20,
            food_category="fast food",
            cuisine_origin="Italian",
            cat_roast="This food should die.",
        )
        with pytest.raises(GuardrailViolation):
            FoodAnalysisGuardrails.validate(analysis)

    def test_roast_with_kill_yourself(self):
        """Roast with 'kys' should fail."""
        analysis = FoodAnalysisResponse(
            food_name="Pizza",
            calories=500,
            protein_g=20,
            carbs_g=60,
            fat_g=20,
            food_category="fast food",
            cuisine_origin="Italian",
            cat_roast="This is bad. kys for eating this.",
        )
        with pytest.raises(GuardrailViolation):
            FoodAnalysisGuardrails.validate(analysis)

    def test_roast_clean_sarcasm(self):
        """Sarcasm without toxic language should pass."""
        analysis = FoodAnalysisResponse(
            food_name="Salad",
            calories=300,
            protein_g=30,
            carbs_g=20,
            fat_g=10,
            food_category="salad",
            cuisine_origin="American",
            cat_roast="Oh wow, finally a vegetable. How shocking.",
        )
        result = FoodAnalysisGuardrails.validate(analysis)
        assert "shocking" in result.cat_roast.lower()

    def test_multiple_forbidden_phrases(self):
        """Detect various forbidden phrases."""
        forbidden_tests = [
            "kill yourself",
            "kys",
            "hate you",
            "should die",
        ]
        for phrase in forbidden_tests:
            analysis = FoodAnalysisResponse(
                food_name="Food",
                calories=300,
                protein_g=20,
                carbs_g=20,
                fat_g=10,
                food_category="test",
                cuisine_origin="test",
                cat_roast=f"This is bad: {phrase}",
            )
            with pytest.raises(GuardrailViolation, match="forbidden phrase"):
                FoodAnalysisGuardrails.validate(analysis)


class TestGuardrailViolation:
    """Test GuardrailViolation exception."""

    def test_get_violation_reason(self):
        """Should extract readable reason from violation."""
        analysis = FoodAnalysisResponse(
            food_name="Food",
            calories=300,
            protein_g=20,
            carbs_g=20,
            fat_g=10,
            food_category="fast food",
            cuisine_origin="Italian",
            cat_roast="This should die.",
        )
        try:
            FoodAnalysisGuardrails.validate(analysis)
            assert False, "Should have raised GuardrailViolation"
        except GuardrailViolation as e:
            reason = FoodAnalysisGuardrails.get_violation_reason(e)
            assert "forbidden" in reason.lower() or "die" in reason.lower()


class TestCompleteValidation:
    """Test full validation scenarios."""

    def test_valid_complete_analysis(self):
        """Complete valid analysis should pass all guards."""
        analysis = FoodAnalysisResponse(
            food_name="Grilled Chicken with Vegetables",
            calories=450,
            protein_g=50,
            carbs_g=30,
            fat_g=12,
            food_category="home-cooked",
            cuisine_origin="American",
            cat_roast="Actually pretty decent. I'm mildly impressed.",
        )
        result = FoodAnalysisGuardrails.validate(analysis)
        assert result.food_name == "Grilled Chicken with Vegetables"
        assert result.calories == 450

    def test_sarcasm_roasts_pass(self):
        """Sarcastic roasts should pass if not toxic."""
        roasts = [
            "Wow, pizza again? I'm shocked.",
            "Finally something green.",
            "You're really committing to this pasta lifestyle.",
            "At least you're consistent.",
        ]
        for roast_text in roasts:
            analysis = FoodAnalysisResponse(
                food_name="Food",
                calories=400,
                protein_g=20,
                carbs_g=50,
                fat_g=15,
                food_category="test",
                cuisine_origin="test",
                cat_roast=roast_text,
            )
            result = FoodAnalysisGuardrails.validate(analysis)
            assert result.cat_roast == roast_text
