"""
Tests for the LLM Router — model selection logic.
"""

import pytest

from src.llm.router import TASK_ROUTES, TaskType, get_model_for_task, get_route, get_temperature_for_task


class TestTaskTypes:
    """Test TaskType enum."""

    def test_task_types_exist(self):
        """All required task types should exist."""
        assert TaskType.ANALYZE_FOOD.value == "analyze_food"
        assert TaskType.RECOMMEND_MEAL.value == "recommend_meal"
        assert TaskType.WEEKLY_RECAP.value == "weekly_recap"


class TestTaskRoutes:
    """Test task-to-model routing."""

    def test_analyze_food_uses_haiku_with_fallback(self):
        """Food analysis should use Haiku with Sonnet fallback."""
        route = get_route(TaskType.ANALYZE_FOOD)
        assert route.primary_model == "claude-haiku-4-5-20251001"
        assert route.fallback_model == "claude-sonnet-4-20250514"
        assert route.max_tokens == 500

    def test_recommend_meal_uses_sonnet(self):
        """Recommendations should use Sonnet."""
        route = get_route(TaskType.RECOMMEND_MEAL)
        assert route.primary_model == "claude-sonnet-4-20250514"
        assert route.max_tokens == 1000

    def test_weekly_recap_uses_sonnet(self):
        """Weekly recaps should use Sonnet."""
        route = get_route(TaskType.WEEKLY_RECAP)
        assert route.primary_model == "claude-sonnet-4-20250514"
        assert route.max_tokens == 1500

    def test_all_tasks_have_routes(self):
        """All TaskType values should have routes defined."""
        for task_type in TaskType:
            route = get_route(task_type)
            assert route.primary_model is not None
            assert route.max_tokens is not None

    def test_routes_have_reasonable_temperatures(self):
        """All routes should have reasonable temperatures."""
        for route in TASK_ROUTES.values():
            assert 0 <= route.temperature <= 2.0
            # Analyze should be less creative than recap
            analyze_temp = get_temperature_for_task(TaskType.ANALYZE_FOOD)
            recap_temp = get_temperature_for_task(TaskType.WEEKLY_RECAP)
            assert analyze_temp < recap_temp


class TestGetModelForTask:
    """Test convenience function to get model name."""

    def test_get_model_for_analyze_food(self):
        """Should return Haiku for food analysis."""
        model = get_model_for_task(TaskType.ANALYZE_FOOD)
        assert model == "claude-haiku-4-5-20251001"

    def test_get_model_for_recommend_meal(self):
        """Should return Sonnet for recommendations."""
        model = get_model_for_task(TaskType.RECOMMEND_MEAL)
        assert model == "claude-sonnet-4-20250514"

    def test_get_model_for_weekly_recap(self):
        """Should return Sonnet for recaps."""
        model = get_model_for_task(TaskType.WEEKLY_RECAP)
        assert model == "claude-sonnet-4-20250514"


class TestGetTemperatureForTask:
    """Test convenience function to get temperature."""

    def test_temperatures_exist(self):
        """All tasks should have defined temperatures."""
        for task_type in TaskType:
            temp = get_temperature_for_task(task_type)
            assert isinstance(temp, (int, float))
            assert temp > 0

    def test_temperature_increases_with_creativity(self):
        """More creative tasks should have higher temperatures."""
        food_temp = get_temperature_for_task(TaskType.ANALYZE_FOOD)
        recommend_temp = get_temperature_for_task(TaskType.RECOMMEND_MEAL)
        recap_temp = get_temperature_for_task(TaskType.WEEKLY_RECAP)

        # Food analysis should be most consistent
        assert food_temp < recommend_temp < recap_temp


class TestUnknownTaskType:
    """Test error handling for unknown tasks."""

    def test_unknown_task_raises_error(self):
        """Should raise ValueError for unknown task type."""
        with pytest.raises(ValueError, match="Unknown task type"):
            get_route("unknown_task")
