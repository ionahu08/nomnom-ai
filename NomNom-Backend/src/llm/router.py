"""
Model Router — Choose the right model for each task.

In Plain English:
- Food photo analysis? Use Haiku (fast + cheap).
- Writing recommendations or recaps? Use Sonnet (smarter).

This keeps costs down while maintaining quality.
"""

from enum import Enum
from typing import Optional


class TaskType(str, Enum):
    """Supported AI task types."""

    ANALYZE_FOOD = "analyze_food"
    RECOMMEND_MEAL = "recommend_meal"
    WEEKLY_RECAP = "weekly_recap"


class ModelRoute:
    """Model configuration for a task."""

    def __init__(
        self,
        primary_model: str,
        fallback_model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
    ):
        """
        Configure a model route.

        Args:
            primary_model: Main model to use (e.g., "claude-haiku-4-5-20251001")
            fallback_model: If primary fails repeatedly, use this model
            max_tokens: Override default max_tokens for this task
            temperature: Sampling temperature (0=deterministic, 1=creative)
        """
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.max_tokens = max_tokens
        self.temperature = temperature


# Task-to-Model Routing Table
TASK_ROUTES = {
    TaskType.ANALYZE_FOOD: ModelRoute(
        primary_model="claude-haiku-4-5-20251001",
        fallback_model="claude-sonnet-4-20250514",
        max_tokens=500,
        temperature=0.7,  # Slightly creative but consistent
    ),
    TaskType.RECOMMEND_MEAL: ModelRoute(
        primary_model="claude-sonnet-4-20250514",
        max_tokens=1000,
        temperature=0.8,  # Conversational and helpful
    ),
    TaskType.WEEKLY_RECAP: ModelRoute(
        primary_model="claude-sonnet-4-20250514",
        max_tokens=1500,
        temperature=0.9,  # Entertaining and witty
    ),
}


def get_route(task_type: TaskType) -> ModelRoute:
    """
    Get the model route for a task.

    Args:
        task_type: The type of task (from TaskType enum)

    Returns:
        ModelRoute with model, max_tokens, temperature, etc.

    Raises:
        ValueError: If task_type is not recognized
    """
    if task_type not in TASK_ROUTES:
        raise ValueError(f"Unknown task type: {task_type}")

    return TASK_ROUTES[task_type]


def get_model_for_task(task_type: TaskType) -> str:
    """Convenience: just get the primary model name for a task."""
    route = get_route(task_type)
    return route.primary_model


def get_temperature_for_task(task_type: TaskType) -> float:
    """Convenience: get temperature for a task."""
    route = get_route(task_type)
    return route.temperature
