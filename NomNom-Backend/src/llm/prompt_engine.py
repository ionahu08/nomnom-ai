"""
Prompt Engine — Render Jinja2 templates with context.

This keeps prompts in files (not hardcoded in Python), making them:
- Easy to version control
- Easy to tweak without redeploying code
- Easy to A/B test different phrasings
"""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)

# Find the prompts directory
PROMPTS_DIR = Path(__file__).parent / "prompts"

# Create Jinja2 environment
jinja_env = Environment(
    loader=FileSystemLoader(str(PROMPTS_DIR)),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False,
)


def render_prompt(template_name: str, **context) -> str:
    """
    Render a Jinja2 prompt template with context.

    Args:
        template_name: Name of the .j2 file (e.g., "analyze_food.j2")
        **context: Variables to inject into the template

    Returns:
        Rendered prompt string

    Raises:
        TemplateNotFound: If template file doesn't exist
        Exception: If template rendering fails
    """
    try:
        template = jinja_env.get_template(template_name)
        logger.debug(f"Rendering template: {template_name} with context keys: {context.keys()}")
        rendered = template.render(**context)
        logger.debug(f"Template rendered successfully")
        return rendered
    except TemplateNotFound as e:
        logger.error(f"Template not found: {template_name}")
        raise
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {str(e)}")
        raise


def render_analyze_food_prompt(cat_style: str) -> str:
    """Render the food analysis prompt."""
    return render_prompt("analyze_food.j2", cat_style=cat_style)


def render_recommend_meal_prompt(
    today_calories: int,
    today_protein: float,
    today_carbs: float,
    today_fat: float,
    target_calories: int,
    target_protein: int,
    target_carbs: int,
    target_fat: int,
    missing_calories: int,
    missing_protein: float,
    missing_carbs: float,
    missing_fat: float,
    dietary_restrictions: list[str] | None = None,
    cuisine_preferences: list[str] | None = None,
    allergies: list[str] | None = None,
    recent_meals: list[dict] | None = None,
    kb_entries: list[dict] | None = None,
) -> str:
    """Render the meal recommendation prompt."""
    return render_prompt(
        "recommend_meal.j2",
        today_calories=today_calories,
        today_protein=today_protein,
        today_carbs=today_carbs,
        today_fat=today_fat,
        target_calories=target_calories,
        target_protein=target_protein,
        target_carbs=target_carbs,
        target_fat=target_fat,
        missing_calories=missing_calories,
        missing_protein=missing_protein,
        missing_carbs=missing_carbs,
        missing_fat=missing_fat,
        dietary_restrictions=dietary_restrictions or [],
        cuisine_preferences=cuisine_preferences or [],
        allergies=allergies or [],
        recent_meals=recent_meals or [],
        kb_entries=kb_entries or [],
    )


def render_weekly_recap_prompt(
    week_start: str,
    week_end: str,
    total_meals_logged: int,
    avg_calories: int,
    best_day: str,
    best_day_calories: int,
    worst_day: str,
    worst_day_calories: int,
    most_eaten_category: str,
    avg_protein: float,
    avg_carbs: float,
    avg_fat: float,
    cat_style: str,
    meals: list[dict] | None = None,
) -> str:
    """Render the weekly recap prompt."""
    return render_prompt(
        "weekly_recap.j2",
        week_start=week_start,
        week_end=week_end,
        total_meals_logged=total_meals_logged,
        avg_calories=avg_calories,
        best_day=best_day,
        best_day_calories=best_day_calories,
        worst_day=worst_day,
        worst_day_calories=worst_day_calories,
        most_eaten_category=most_eaten_category,
        avg_protein=avg_protein,
        avg_carbs=avg_carbs,
        avg_fat=avg_fat,
        cat_style=cat_style,
        meals=meals or [],
    )
