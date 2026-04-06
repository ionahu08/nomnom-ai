"""
Tests for the Prompt Engine — Jinja2 template rendering.
"""

import pytest

from src.llm.prompt_engine import (
    render_analyze_food_prompt,
    render_prompt,
    render_recommend_meal_prompt,
    render_weekly_recap_prompt,
)


class TestRenderPrompt:
    """Test basic prompt rendering."""

    def test_render_analyze_food_with_sassy_cat(self):
        """Should render analyze_food template with sassy cat persona."""
        prompt = render_analyze_food_prompt(cat_style="sassy")
        assert "sassy" in prompt.lower()
        assert "JSON" in prompt
        assert "food_name" in prompt

    def test_render_analyze_food_with_grumpy_cat(self):
        """Should render with grumpy cat persona."""
        prompt = render_analyze_food_prompt(cat_style="grumpy")
        assert "grumpy" in prompt.lower()
        assert "JSON" in prompt

    def test_render_analyze_food_with_wholesome_cat(self):
        """Should render with wholesome cat persona."""
        prompt = render_analyze_food_prompt(cat_style="wholesome")
        assert "wholesome" in prompt.lower() or "encouraging" in prompt.lower()
        assert "JSON" in prompt

    def test_render_analyze_food_with_concerned_cat(self):
        """Should render with concerned cat persona."""
        prompt = render_analyze_food_prompt(cat_style="concerned")
        assert "concerned" in prompt.lower() or "worry" in prompt.lower()
        assert "JSON" in prompt

    def test_render_analyze_food_includes_examples(self):
        """Should include few-shot examples."""
        prompt = render_analyze_food_prompt(cat_style="sassy")
        assert "Big Mac" in prompt
        assert "Salad" in prompt
        assert "Sushi" in prompt

    def test_render_analyze_food_includes_json_format(self):
        """Should include JSON schema."""
        prompt = render_analyze_food_prompt(cat_style="sassy")
        assert "calories" in prompt
        assert "protein_g" in prompt
        assert "carbs_g" in prompt
        assert "fat_g" in prompt
        assert "food_category" in prompt
        assert "cuisine_origin" in prompt
        assert "cat_roast" in prompt


class TestRenderRecommendationPrompt:
    """Test meal recommendation prompt rendering."""

    def test_render_recommend_meal_includes_nutrition_data(self):
        """Should include current nutrition intake."""
        prompt = render_recommend_meal_prompt(
            today_calories=1500,
            today_protein=50,
            today_carbs=100,
            today_fat=40,
            target_calories=2000,
            target_protein=150,
            target_carbs=250,
            target_fat=70,
            missing_calories=500,
            missing_protein=100,
            missing_carbs=150,
            missing_fat=30,
        )
        assert "1500" in prompt  # Today's calories
        assert "2000" in prompt  # Target calories
        assert "50" in prompt  # Today's protein

    def test_render_recommend_meal_includes_restrictions(self):
        """Should include dietary restrictions."""
        prompt = render_recommend_meal_prompt(
            today_calories=1500,
            today_protein=50,
            today_carbs=100,
            today_fat=40,
            target_calories=2000,
            target_protein=150,
            target_carbs=250,
            target_fat=70,
            missing_calories=500,
            missing_protein=100,
            missing_carbs=150,
            missing_fat=30,
            dietary_restrictions=["vegetarian", "gluten-free"],
        )
        assert "vegetarian" in prompt
        assert "gluten-free" in prompt

    def test_render_recommend_meal_includes_preferences(self):
        """Should include cuisine preferences."""
        prompt = render_recommend_meal_prompt(
            today_calories=1500,
            today_protein=50,
            today_carbs=100,
            today_fat=40,
            target_calories=2000,
            target_protein=150,
            target_carbs=250,
            target_fat=70,
            missing_calories=500,
            missing_protein=100,
            missing_carbs=150,
            missing_fat=30,
            cuisine_preferences=["Japanese", "Italian"],
        )
        assert "Japanese" in prompt
        assert "Italian" in prompt

    def test_render_recommend_meal_with_recent_meals(self):
        """Should include recent meals."""
        recent_meals = [
            {"food_name": "Chicken Sandwich", "calories": 450, "protein_g": 35},
            {"food_name": "Apple", "calories": 80, "protein_g": 0},
        ]
        prompt = render_recommend_meal_prompt(
            today_calories=1500,
            today_protein=50,
            today_carbs=100,
            today_fat=40,
            target_calories=2000,
            target_protein=150,
            target_carbs=250,
            target_fat=70,
            missing_calories=500,
            missing_protein=100,
            missing_carbs=150,
            missing_fat=30,
            recent_meals=recent_meals,
        )
        assert "Chicken Sandwich" in prompt
        assert "Apple" in prompt

    def test_render_recommend_meal_with_kb_entries(self):
        """Should include knowledge base entries."""
        kb_entries = [
            {"title": "Protein Tips", "content": "Eat more eggs and fish"},
            {"title": "Carb Balance", "content": "Prefer whole grains"},
        ]
        prompt = render_recommend_meal_prompt(
            today_calories=1500,
            today_protein=50,
            today_carbs=100,
            today_fat=40,
            target_calories=2000,
            target_protein=150,
            target_carbs=250,
            target_fat=70,
            missing_calories=500,
            missing_protein=100,
            missing_carbs=150,
            missing_fat=30,
            kb_entries=kb_entries,
        )
        assert "Protein Tips" in prompt
        assert "Carb Balance" in prompt


class TestRenderWeeklyRecapPrompt:
    """Test weekly recap prompt rendering."""

    def test_render_weekly_recap_includes_dates(self):
        """Should include week dates."""
        prompt = render_weekly_recap_prompt(
            week_start="2025-02-03",
            week_end="2025-02-09",
            total_meals_logged=21,
            avg_calories=2000,
            best_day="Friday",
            best_day_calories=2300,
            worst_day="Monday",
            worst_day_calories=1500,
            most_eaten_category="pizza",
            avg_protein=150,
            avg_carbs=250,
            avg_fat=70,
            cat_style="sassy",
        )
        assert "2025-02-03" in prompt
        assert "2025-02-09" in prompt

    def test_render_weekly_recap_includes_stats(self):
        """Should include nutrition statistics."""
        prompt = render_weekly_recap_prompt(
            week_start="2025-02-03",
            week_end="2025-02-09",
            total_meals_logged=21,
            avg_calories=2000,
            best_day="Friday",
            best_day_calories=2300,
            worst_day="Monday",
            worst_day_calories=1500,
            most_eaten_category="pizza",
            avg_protein=150,
            avg_carbs=250,
            avg_fat=70,
            cat_style="sassy",
        )
        assert "21" in prompt  # meals logged
        assert "2000" in prompt  # avg calories
        assert "Friday" in prompt  # best day
        assert "pizza" in prompt  # most eaten

    def test_render_weekly_recap_includes_cat_style(self):
        """Should include cat personality."""
        prompt = render_weekly_recap_prompt(
            week_start="2025-02-03",
            week_end="2025-02-09",
            total_meals_logged=21,
            avg_calories=2000,
            best_day="Friday",
            best_day_calories=2300,
            worst_day="Monday",
            worst_day_calories=1500,
            most_eaten_category="pizza",
            avg_protein=150,
            avg_carbs=250,
            avg_fat=70,
            cat_style="grumpy",
        )
        assert "grumpy" in prompt.lower()

    def test_render_weekly_recap_with_meals(self):
        """Should include meal list."""
        meals = [
            {"food_name": "Pizza", "logged_at": "2025-02-03"},
            {"food_name": "Salad", "logged_at": "2025-02-04"},
        ]
        prompt = render_weekly_recap_prompt(
            week_start="2025-02-03",
            week_end="2025-02-09",
            total_meals_logged=21,
            avg_calories=2000,
            best_day="Friday",
            best_day_calories=2300,
            worst_day="Monday",
            worst_day_calories=1500,
            most_eaten_category="pizza",
            avg_protein=150,
            avg_carbs=250,
            avg_fat=70,
            cat_style="sassy",
            meals=meals,
        )
        assert "Pizza" in prompt
        assert "Salad" in prompt


class TestTemplateErrors:
    """Test error handling."""

    def test_render_nonexistent_template(self):
        """Should raise error for missing template."""
        with pytest.raises(Exception):  # TemplateNotFound
            render_prompt("nonexistent_template.j2")

    def test_render_with_invalid_context(self):
        """Should handle missing context variables gracefully."""
        # Jinja2 templates usually don't error on missing vars, they just render empty
        # So this test verifies that behavior
        prompt = render_prompt("cat_personas.j2", cat_style="sassy")
        assert isinstance(prompt, str)


class TestTemplateIntegration:
    """Integration tests combining router and prompt engine."""

    def test_analyze_food_template_has_json_schema(self):
        """Food analysis should output valid JSON schema."""
        prompt = render_analyze_food_prompt(cat_style="sassy")
        # Check for required JSON fields
        required_fields = [
            "food_name",
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "food_category",
            "cuisine_origin",
            "cat_roast",
        ]
        for field in required_fields:
            assert field in prompt

    def test_all_cat_styles_render(self):
        """All cat styles should render without error."""
        cat_styles = ["sassy", "grumpy", "wholesome", "concerned", "neutral"]
        for style in cat_styles:
            prompt = render_analyze_food_prompt(cat_style=style)
            assert isinstance(prompt, str)
            assert len(prompt) > 0
