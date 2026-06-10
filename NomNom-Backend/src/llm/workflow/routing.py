"""
Intent Router — Classify user requests into intents.

Maps user inputs to appropriate workflow handlers.
Intents:
  - "recommend" → "What should I eat?" (use MealRecommendationWorkflow)
  - "query" → "What did I eat?" or "How am I doing?" (use simple RAG)
  - "other" → Fallback to default handler
"""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    """User request intents."""
    RECOMMEND = "recommend"      # What should I eat next?
    QUERY = "query"              # What did I eat? Status check?
    OTHER = "other"              # Unknown intent


class IntentRouter:
    """
    Classify user requests into intents.

    Simple keyword-based routing (could be upgraded to LLM-based).
    """

    # Keywords for each intent
    RECOMMEND_KEYWORDS = {
        "should i eat",
        "what should i eat",
        "recommend",
        "suggestion",
        "what to eat",
        "meal idea",
        "next meal",
        "what's for",
        "help me eat",
    }

    QUERY_KEYWORDS = {
        "what did i eat",
        "food log",
        "meals today",
        "how am i doing",
        "am i hitting",
        "nutrition",
        "macro",
        "calorie",
        "progress",
        "status",
    }

    def classify(self, user_input: str) -> Intent:
        """
        Classify user input into an intent.

        Args:
            user_input: Raw user message

        Returns:
            Intent enum value

        Example:
            >>> router = IntentRouter()
            >>> router.classify("What should I eat for dinner?")
            <Intent.RECOMMEND: 'recommend'>
        """
        user_lower = user_input.lower().strip()

        # Check recommend keywords
        if any(keyword in user_lower for keyword in self.RECOMMEND_KEYWORDS):
            logger.debug(f"Classified as RECOMMEND: {user_input[:50]}...")
            return Intent.RECOMMEND

        # Check query keywords
        if any(keyword in user_lower for keyword in self.QUERY_KEYWORDS):
            logger.debug(f"Classified as QUERY: {user_input[:50]}...")
            return Intent.QUERY

        # Default to OTHER
        logger.debug(f"Classified as OTHER: {user_input[:50]}...")
        return Intent.OTHER

    def get_handler_name(self, intent: Intent) -> str:
        """
        Get the handler function name for an intent.

        Args:
            intent: Intent enum

        Returns:
            Handler function name (e.g., "handle_recommend")
        """
        return f"handle_{intent.value}"
