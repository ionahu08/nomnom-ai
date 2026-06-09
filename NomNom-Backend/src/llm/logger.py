"""
AI Call Logger — Track every AI API call for observability.

This logs to the ai_call_logs table so we can:
- Monitor API costs
- Track latency
- Measure accuracy (user corrections)
- Detect rate limit violations
- Optimize model selection
"""

import logging
import time
from typing import Optional

import anthropic

logger = logging.getLogger(__name__)


class AICallLogger:
    """Log AI API calls to database (async)."""

    # Token pricing (USD per million tokens)
    # https://www.anthropic.com/pricing/claude
    PRICING = {
        "claude-haiku-4-5-20251001": {
            "input": 0.80,        # $0.80 per 1M input tokens
            "output": 4.00,       # $4.00 per 1M output tokens
            "cache_creation": 1.00,    # 25% premium
            "cache_read": 0.08,        # 90% discount
        },
        "claude-sonnet-4-20250514": {
            "input": 3.00,        # $3.00 per 1M input tokens
            "output": 15.00,      # $15.00 per 1M output tokens
            "cache_creation": 3.75,    # 25% premium
            "cache_read": 0.30,        # 90% discount
        },
        "claude-opus-4-7": {
            "input": 15.00,       # $15.00 per 1M input tokens
            "output": 75.00,      # $75.00 per 1M output tokens
            "cache_creation": 18.75,   # 25% premium
            "cache_read": 1.50,        # 90% discount
        },
    }

    @staticmethod
    def estimate_cost(
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_creation_tokens: int = 0,
        cache_read_tokens: int = 0,
    ) -> float:
        """
        Estimate API cost for an LLM call, including cache token pricing.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cache_creation_tokens: Tokens used to create cache (25% premium)
            cache_read_tokens: Tokens read from cache (90% discount)

        Returns:
            Estimated cost in USD
        """
        if model not in AICallLogger.PRICING:
            raise ValueError(f"Unknown model for pricing: {model}. Add to PRICING dict.")

        pricing = AICallLogger.PRICING[model]

        # Regular input/output tokens
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        # Cache tokens use separate pricing (25% premium to create, 90% discount to read)
        cache_creation_cost = (cache_creation_tokens / 1_000_000) * pricing.get("cache_creation", pricing["input"] * 1.25)
        cache_read_cost = (cache_read_tokens / 1_000_000) * pricing.get("cache_read", pricing["input"] * 0.10)

        total_cost = input_cost + output_cost + cache_creation_cost + cache_read_cost

        return round(total_cost, 6)

    @staticmethod
    def extract_token_usage(response: anthropic.types.Message) -> tuple[int, int]:
        """
        Extract token usage from API response.

        Args:
            response: Anthropic API response

        Returns:
            Tuple of (input_tokens, output_tokens)
        """
        if not hasattr(response, "usage"):
            logger.warning("Response has no usage information")
            return 0, 0

        input_tokens = response.usage.input_tokens if hasattr(response.usage, "input_tokens") else 0
        output_tokens = response.usage.output_tokens if hasattr(response.usage, "output_tokens") else 0

        return input_tokens, output_tokens

    @staticmethod
    def log_call(
        model: str,
        task_type: str,
        response: Optional[anthropic.types.Message],
        latency_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
        user_id: Optional[int] = None,
        cached: bool = False,
    ) -> dict:
        """
        Create a log entry for an AI call.

        Args:
            model: Model name
            task_type: Task type (e.g., "analyze_food")
            response: API response (or None if failed)
            latency_ms: Call latency in milliseconds
            success: Whether the call succeeded
            error_message: Error message if failed
            user_id: User ID if applicable
            cached: Whether result was cached

        Returns:
            Dictionary with log entry data (ready to save to DB)
        """
        input_tokens = 0
        output_tokens = 0
        cache_creation_tokens = 0
        cache_read_tokens = 0

        if response:
            input_tokens, output_tokens = AICallLogger.extract_token_usage(response)
            cache_creation_tokens = getattr(response.usage, "cache_creation_input_tokens", 0)
            cache_read_tokens = getattr(response.usage, "cache_read_input_tokens", 0)

        estimated_cost = AICallLogger.estimate_cost(
            model,
            input_tokens,
            output_tokens,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_tokens=cache_read_tokens,
        )

        log_entry = {
            "model": model,
            "task_type": task_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": int(latency_ms),
            "estimated_cost": estimated_cost,
            "success": success,
            "error_message": error_message,
            "user_id": user_id,
            "cached": cached,
        }

        logger.info(
            f"AI call logged: {model} / {task_type}",
            extra={
                "tokens": f"{input_tokens}+{output_tokens}",
                "latency_ms": int(latency_ms),
                "cost": f"${estimated_cost:.6f}",
                "success": success,
            },
        )

        return log_entry


class TimerContext:
    """Context manager to measure latency."""

    def __init__(self):
        """Initialize timer."""
        self.start_time = None
        self.elapsed_ms = 0

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and calculate elapsed time."""
        if self.start_time:
            self.elapsed_ms = (time.time() - self.start_time) * 1000
        return False
