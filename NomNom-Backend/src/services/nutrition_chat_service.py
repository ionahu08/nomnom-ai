import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from anthropic import Anthropic

from src.models.nutrition_chat import NutritionChatMessage
from src.models.user import User
from src.repositories.analytics_repository import AnalyticsRepository
from src.llm.nutrition_coach_prompt import get_nutrition_coach_prompt

logger = logging.getLogger(__name__)


class NutritionChatService:
    """Service for managing nutrition chatbot conversations."""

    @staticmethod
    async def get_chat_history(db: AsyncSession, user_id: int, limit: int = 50) -> list[NutritionChatMessage]:
        """Fetch chat message history for a user."""
        query = (
            select(NutritionChatMessage)
            .where(NutritionChatMessage.user_id == user_id)
            .order_by(NutritionChatMessage.created_at)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def save_message(
        db: AsyncSession, user_id: int, role: str, content: str
    ) -> NutritionChatMessage:
        """Save a chat message to the database."""
        message = NutritionChatMessage(user_id=user_id, role=role, content=content)
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def gather_context(
        db: AsyncSession, user: User
    ) -> dict:
        """Gather user context for the nutrition coach prompt."""
        # Fetch user's health profile (already loaded by dependency, avoid extra refresh)
        user_profile = user.profile

        # Get nutrition data for the past week
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        # Fetch aggregated stats for the week
        stats = await AnalyticsRepository.get_aggregated_stats(
            db, user.id, start_date, end_date
        )

        # Fetch user targets
        targets = await AnalyticsRepository.get_user_targets(db, user.id)

        # Get days logged
        days_logged, total_days = await AnalyticsRepository.get_days_logged(
            db, user.id, start_date, end_date
        )

        # Fetch food logs to get food names
        food_logs = await AnalyticsRepository.get_food_logs_for_period(
            db, user.id, start_date, end_date
        )

        # Extract unique foods from logs
        foods = list(set(log.food_name for log in food_logs if log.food_name))[:20]

        # Build context dictionary
        context = {
            "user_goal": user_profile.goal if user_profile else None,
            "user_allergies": user_profile.allergies if user_profile else None,
            "user_medical_conditions": user_profile.medical_conditions if user_profile else None,
            "user_age": user_profile.age if user_profile else None,
            "user_height_cm": user_profile.height_cm if user_profile else None,
            "user_weight_kg": user_profile.weight_kg if user_profile else None,
            "calorie_target": targets.get("calorie_target", 2000),
            "protein_target": targets.get("protein_target", 150),
            "carb_target": targets.get("carb_target", 200),
            "fat_target": targets.get("fat_target", 65),
            "calories_this_week": stats.get("calories", {}).get("total", 0),
            "protein_this_week": stats.get("protein", {}).get("total", 0),
            "carbs_this_week": stats.get("carbs", {}).get("total", 0),
            "fat_this_week": stats.get("fat", {}).get("total", 0),
            "days_logged": days_logged,
            "total_days": total_days,
            "recent_foods": foods,
        }

        return context

    @staticmethod
    async def get_chat_response(
        db: AsyncSession, user: User, user_message: str
    ) -> Optional[str]:
        """Get a chat response from Claude based on user message and context."""
        try:
            # Gather user context
            context = await NutritionChatService.gather_context(db, user)

            # Get chat history for conversation continuity (last 5 messages)
            history = await NutritionChatService.get_chat_history(db, user.id, limit=5)

            # Build conversation messages
            messages = []

            # Add recent chat history
            for msg in history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Get system prompt customized for this user
            system_prompt = get_nutrition_coach_prompt(context)

            # Call Claude API
            client = Anthropic()
            response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=512,
                system=system_prompt,
                messages=messages,
            )

            # Extract response text
            response_text = response.content[0].text
            logger.info(f"[NutritionChat] Generated response: {response_text[:100]}...")
            return response_text

        except Exception as e:
            logger.error(f"[NutritionChat] Error getting chat response: {e}")
            logger.exception(f"[NutritionChat] Full traceback: {e}")
            return None
