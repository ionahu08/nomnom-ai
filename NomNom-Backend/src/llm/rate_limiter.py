"""
Rate Limiter — Prevent per-user API call abuse.

Limits:
- analyze_food: 30 calls/hour per user
- recommend_meal: 10 calls/hour per user
- Default: 100 calls/hour per user

Prevents:
- Runaway costs (5000 calls = $2000 Haiku costs)
- DoS-like behavior
- Accidental loops

In production, this would query Redis for sliding window counters.
For now, we provide the interface so it integrates cleanly later.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when user exceeds rate limit."""

    pass


class RateLimiter:
    """Per-user rate limiter for AI calls."""

    # Limits per task type (calls per hour)
    LIMITS = {
        "analyze_food": 30,
        "recommend_meal": 10,
        "weekly_recap": 5,
    }

    DEFAULT_LIMIT = 100

    @staticmethod
    async def check_limit(
        user_id: int,
        task_type: str,
    ) -> bool:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User ID
            task_type: Task type (e.g., "analyze_food")

        Returns:
            True if within limit, raises RateLimitExceeded if over limit

        Note:
        In production, this would:
        1. Query Redis for call count in last hour
        2. Increment counter
        3. Set expiry to 1 hour
        4. Raise RateLimitExceeded if limit exceeded

        For now, always returns True (no limiting).
        """
        # TODO: Implement with Redis when integrated
        # call_count = await redis.get(f"rate_limit:{user_id}:{task_type}")
        # if call_count and call_count >= RateLimiter.get_limit(task_type):
        #     raise RateLimitExceeded(
        #         f"User {user_id} exceeded rate limit for {task_type}"
        #     )
        # await redis.incr(f"rate_limit:{user_id}:{task_type}")
        # await redis.expire(f"rate_limit:{user_id}:{task_type}", 3600)
        return True

    @staticmethod
    def get_limit(task_type: str) -> int:
        """Get rate limit for a task type."""
        return RateLimiter.LIMITS.get(task_type, RateLimiter.DEFAULT_LIMIT)

    @staticmethod
    def get_limit_message(task_type: str) -> str:
        """Get user-friendly rate limit message."""
        limit = RateLimiter.get_limit(task_type)
        return f"Rate limit: {limit} calls per hour for {task_type}"
