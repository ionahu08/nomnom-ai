"""
Tests for rate limiting.
"""

import pytest

from src.llm.rate_limiter import RateLimitExceeded, RateLimiter


class TestRateLimits:
    """Test rate limit configuration."""

    def test_analyze_food_limit(self):
        """Analyze food should have 30 calls/hour limit."""
        assert RateLimiter.get_limit("analyze_food") == 30

    def test_recommend_meal_limit(self):
        """Recommend meal should have 10 calls/hour limit."""
        assert RateLimiter.get_limit("recommend_meal") == 10

    def test_weekly_recap_limit(self):
        """Weekly recap should have 5 calls/hour limit."""
        assert RateLimiter.get_limit("weekly_recap") == 5

    def test_unknown_task_uses_default(self):
        """Unknown task should use default limit."""
        assert RateLimiter.get_limit("unknown_task") == RateLimiter.DEFAULT_LIMIT

    def test_limits_are_reasonable(self):
        """Limits should prevent runaway costs."""
        for limit in RateLimiter.LIMITS.values():
            assert limit > 0
            assert limit <= 100  # No task should have unlimited access


class TestLimitMessages:
    """Test user-friendly limit messages."""

    def test_limit_message_format(self):
        """Limit message should be readable."""
        msg = RateLimiter.get_limit_message("analyze_food")
        assert "Rate limit" in msg
        assert "30" in msg
        assert "analyze_food" in msg

    def test_all_tasks_have_messages(self):
        """All task types should have messages."""
        for task in ["analyze_food", "recommend_meal", "weekly_recap"]:
            msg = RateLimiter.get_limit_message(task)
            assert len(msg) > 0
            assert task in msg


class TestRateLimiterCheck:
    """Test rate limit checking."""

    @pytest.mark.asyncio
    async def test_check_limit_allows_within_limit(self):
        """Checking within limit should return True."""
        result = await RateLimiter.check_limit(user_id=1, task_type="analyze_food")
        assert result is True

    @pytest.mark.asyncio
    async def test_check_limit_for_different_users(self):
        """Different users should have separate limits."""
        result1 = await RateLimiter.check_limit(user_id=1, task_type="analyze_food")
        result2 = await RateLimiter.check_limit(user_id=2, task_type="analyze_food")
        assert result1 is True
        assert result2 is True
