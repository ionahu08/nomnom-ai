"""
Workflow Recommendation Service — Integrates workflow with existing API.

This service wraps MealRecommendationWorkflow and adapts its output
to the existing MealRecommendationResponse format.

Usage:
    service = WorkflowRecommendationService(llm_client, db)
    result = await service.get_meal_recommendation(user_id, use_workflow=True)

This allows gradual rollout: existing code uses old path, new code
can opt into workflow with ?use_workflow=true query param.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.llm.client import LLMClient
from src.llm.workflow.meal_recommendation_workflow import (
    MealRecommendationWorkflow,
    WorkflowInput,
)
from src.llm.workflow.routing import IntentRouter, Intent
from src.models.user import User
from src.schemas.recommendation import MealRecommendationResponse
from src.services.profile_service import get_profile, get_effective_targets
from src.services.food_log_service import list_today_logs

logger = logging.getLogger(__name__)


class WorkflowRecommendationService:
    """
    Recommendation service using workflow pattern.

    Integrates the 5-step workflow with existing NomNom API.
    """

    def __init__(self, llm_client: LLMClient, db: AsyncSession):
        """
        Initialize service.

        Args:
            llm_client: LLMClient instance
            db: Database session
        """
        self.llm_client = llm_client
        self.db = db
        self.intent_router = IntentRouter()
        self.workflow = MealRecommendationWorkflow(llm_client, db)

    async def get_meal_recommendation(
        self, user: User, use_workflow: bool = False
    ) -> MealRecommendationResponse:
        """
        Get meal recommendation using workflow pattern (if enabled).

        Args:
            user: Authenticated user
            use_workflow: If True, use new workflow; else use legacy path

        Returns:
            MealRecommendationResponse with recommendation(s)
        """
        if not use_workflow:
            raise NotImplementedError(
                "Legacy path not implemented in this service. "
                "Use use_workflow=True or call old recommendation service."
            )

        logger.info(f"Getting recommendation for user {user.id} with workflow")

        try:
            # Get user profile and targets
            profile = await get_profile(self.db, user.id)
            if profile is None:
                raise ValueError("User profile not found")

            targets = get_effective_targets(profile)

            # Get today's logs
            today_logs = await list_today_logs(self.db, user.id)

            # Build workflow input
            workflow_input = WorkflowInput(
                user_profile=profile,
                today_logs=today_logs,
                target_calories=targets.calorie_target,
                target_protein=targets.protein_target,
                target_carbs=targets.carb_target,
                target_fat=targets.fat_target,
            )

            # Execute workflow
            workflow_output = await self.workflow.execute(workflow_input)

            # Convert workflow output to API response format
            # Build recommendation text from top 3 options
            recommendation_lines = [workflow_output.reasoning, ""]

            for i, option in enumerate(workflow_output.top_3_options, 1):
                recommendation_lines.append(
                    f"{i}. **{option.meal_name}**\n"
                    f"   - Calories: {option.calories}\n"
                    f"   - Protein: {option.protein_g}g, "
                    f"Carbs: {option.carbs_g}g, Fat: {option.fat_g}g\n"
                    f"   - Why: {option.reasoning}"
                )

            recommendation_text = "\n".join(recommendation_lines)

            logger.info(
                f"Generated workflow recommendation for user {user.id}",
                extra={"user_id": user.id},
            )

            return MealRecommendationResponse(
                recommendation=recommendation_text,
                kb_entries_used=0,  # Track if needed
            )

        except ValueError as e:
            logger.error(f"Validation error: {e}", extra={"user_id": user.id})
            raise
        except Exception as e:
            logger.error(
                f"Error in workflow recommendation: {e}",
                exc_info=True,
                extra={"user_id": user.id},
            )
            raise
