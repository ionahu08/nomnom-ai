"""
Recommendations API — RAG-powered meal suggestions using knowledge base.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.recommendation import MealRecommendationResponse
from src.services.knowledge_service import get_relevant_nutrition_entries
from src.services.profile_service import get_effective_targets, get_profile
from src.services.food_log_service import list_today_logs
from src.services.ai_service import analyze_food_photo
from src.llm.router import TaskType, get_route
from src.llm.prompt_engine import render_recommend_meal_prompt
from src.llm.client import LLMClient
from src.llm.tools import get_tools_for_task
from src.config import settings

logger = logging.getLogger(__name__)
llm_client = LLMClient(api_key=settings.anthropic_api_key)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.get("/meal", response_model=MealRecommendationResponse)
async def get_meal_recommendation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a RAG-powered meal recommendation based on today's nutrition.

    Uses the knowledge base to provide context-aware suggestions
    that fill the user's remaining macro targets for the day.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        MealRecommendationResponse with personalized recommendation
    """
    try:
        # Step 1: Get user profile and targets
        profile = await get_profile(db, current_user.id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User profile not found. Please complete your profile first.",
            )

        targets = get_effective_targets(profile)

        # Step 2: Get today's food logs
        today_logs = await list_today_logs(db, current_user.id)

        # Calculate today's totals
        today_calories = sum(log.calories for log in today_logs)
        today_protein = sum(log.protein_g for log in today_logs)
        today_carbs = sum(log.carbs_g for log in today_logs)
        today_fat = sum(log.fat_g for log in today_logs)

        # Calculate remaining macros
        missing_calories = max(0, targets.calorie_target - today_calories)
        missing_protein = max(0, targets.protein_target - today_protein)
        missing_carbs = max(0, targets.carb_target - today_carbs)
        missing_fat = max(0, targets.fat_target - today_fat)

        # Step 3: Build a query describing what the user needs
        if missing_calories <= 0:
            # User has met or exceeded calorie target
            query = "low calorie meal for the end of the day"
        else:
            parts = []
            if missing_protein > 20:
                parts.append(f"{missing_protein}g protein")
            if missing_carbs > 30:
                parts.append(f"{missing_carbs}g carbs")
            if missing_fat > 10:
                parts.append(f"{missing_fat}g fat")

            query = f"meal with {', '.join(parts)}" if parts else "balanced meal"

        # Step 4: Retrieve relevant nutrition knowledge (RAG)
        kb_entries = await get_relevant_nutrition_entries(db, query, limit=5)

        logger.info(
            f"Retrieved {len(kb_entries)} KB entries for user {current_user.id}",
            extra={"user_id": current_user.id, "query": query},
        )

        # Step 5: Render recommendation prompt with RAG context
        system_prompt = render_recommend_meal_prompt(
            today_calories=today_calories,
            today_protein=today_protein,
            today_carbs=today_carbs,
            today_fat=today_fat,
            target_calories=targets.calorie_target,
            target_protein=targets.protein_target,
            target_carbs=targets.carb_target,
            target_fat=targets.fat_target,
            missing_calories=missing_calories,
            missing_protein=missing_protein,
            missing_carbs=missing_carbs,
            missing_fat=missing_fat,
            dietary_restrictions=profile.dietary_restrictions or [],
            cuisine_preferences=profile.cuisine_preferences or [],
            allergies=profile.allergies or [],
            recent_meals=[
                {
                    "food_name": log.food_name,
                    "calories": log.calories,
                    "protein_g": log.protein_g,
                }
                for log in today_logs[-5:]  # Last 5 meals
            ],
            kb_entries=kb_entries,  # RAG context
        )

        # Step 6: Get route and call LLM (recommendations use Sonnet for quality)
        route = get_route(TaskType.RECOMMEND_MEAL)
        tools = get_tools_for_task(TaskType.RECOMMEND_MEAL.value)

        message = f"Based on my nutrition today, what should I eat next?\n\nI still need {missing_calories} calories, {missing_protein}g protein, {missing_carbs}g carbs, {missing_fat}g fat."

        response = await llm_client.create_message_with_retry(
            model=route.primary_model,
            messages=[{"role": "user", "content": message}],
            system=system_prompt,
            max_tokens=route.max_tokens,
            temperature=route.temperature,
        )

        recommendation_text = response.content[0].text

        logger.info(
            f"Generated recommendation for user {current_user.id}",
            extra={"user_id": current_user.id, "kb_entries": len(kb_entries)},
        )

        return MealRecommendationResponse(
            recommendation=recommendation_text,
            kb_entries_used=len(kb_entries),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error generating recommendation: {e}", exc_info=True, extra={"user_id": current_user.id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendation. Please try again.",
        )
