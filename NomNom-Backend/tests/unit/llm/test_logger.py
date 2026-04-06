"""
Tests for AI call logging.
"""

from unittest.mock import MagicMock

import anthropic
import pytest

from src.llm.logger import AICallLogger, TimerContext


class TestPricing:
    """Test cost estimation."""

    def test_haiku_pricing(self):
        """Haiku should use correct pricing."""
        # 1M input tokens at $0.80, 1M output at $4.00 = $4.80
        cost = AICallLogger.estimate_cost("claude-haiku-4-5-20251001", 1_000_000, 1_000_000)
        assert cost == pytest.approx(4.80, rel=1e-2)

    def test_sonnet_pricing(self):
        """Sonnet should use correct pricing."""
        # 1M input tokens at $3.00, 1M output at $15.00 = $18.00
        cost = AICallLogger.estimate_cost("claude-sonnet-4-20250514", 1_000_000, 1_000_000)
        assert cost == pytest.approx(18.00, rel=1e-2)

    def test_realistic_cost_estimate(self):
        """Test realistic token usage."""
        # Typical food analysis: 100 input, 50 output tokens
        cost = AICallLogger.estimate_cost("claude-haiku-4-5-20251001", 100, 50)
        # 100 * 0.80 / 1M + 50 * 4.00 / 1M
        expected = (100 * 0.80 + 50 * 4.00) / 1_000_000
        assert cost == pytest.approx(expected, rel=1e-5)

    def test_zero_tokens(self):
        """Zero tokens should cost zero."""
        cost = AICallLogger.estimate_cost("claude-haiku-4-5-20251001", 0, 0)
        assert cost == 0.0

    def test_unknown_model_returns_zero(self):
        """Unknown model should return zero cost (with warning)."""
        cost = AICallLogger.estimate_cost("unknown-model", 100, 100)
        assert cost == 0.0


class TestTokenExtraction:
    """Test token usage extraction from responses."""

    def test_extract_token_usage(self):
        """Should extract tokens from response."""
        response = MagicMock(spec=anthropic.types.Message)
        response.usage = MagicMock()
        response.usage.input_tokens = 100
        response.usage.output_tokens = 50

        input_tokens, output_tokens = AICallLogger.extract_token_usage(response)
        assert input_tokens == 100
        assert output_tokens == 50

    def test_extract_token_usage_missing_usage(self):
        """Should handle missing usage information."""
        response = MagicMock(spec=anthropic.types.Message)
        del response.usage

        input_tokens, output_tokens = AICallLogger.extract_token_usage(response)
        assert input_tokens == 0
        assert output_tokens == 0

    def test_extract_token_usage_missing_fields(self):
        """Should handle missing token fields."""
        response = MagicMock(spec=anthropic.types.Message)
        response.usage = MagicMock()
        del response.usage.input_tokens
        del response.usage.output_tokens

        input_tokens, output_tokens = AICallLogger.extract_token_usage(response)
        assert input_tokens == 0
        assert output_tokens == 0


class TestLogEntry:
    """Test log entry creation."""

    def test_successful_call_log(self):
        """Should create log entry for successful call."""
        response = MagicMock(spec=anthropic.types.Message)
        response.usage = MagicMock(input_tokens=100, output_tokens=50)

        log_entry = AICallLogger.log_call(
            model="claude-haiku-4-5-20251001",
            task_type="analyze_food",
            response=response,
            latency_ms=1234.5,
            success=True,
            user_id=42,
        )

        assert log_entry["model"] == "claude-haiku-4-5-20251001"
        assert log_entry["task_type"] == "analyze_food"
        assert log_entry["input_tokens"] == 100
        assert log_entry["output_tokens"] == 50
        assert log_entry["latency_ms"] == 1234
        assert log_entry["success"] is True
        assert log_entry["user_id"] == 42
        assert log_entry["cached"] is False
        assert log_entry["error_message"] is None
        assert log_entry["estimated_cost"] > 0

    def test_failed_call_log(self):
        """Should create log entry for failed call."""
        log_entry = AICallLogger.log_call(
            model="claude-haiku-4-5-20251001",
            task_type="analyze_food",
            response=None,
            latency_ms=500,
            success=False,
            error_message="Timeout after 10s",
            user_id=42,
        )

        assert log_entry["success"] is False
        assert log_entry["error_message"] == "Timeout after 10s"
        assert log_entry["input_tokens"] == 0
        assert log_entry["output_tokens"] == 0
        assert log_entry["estimated_cost"] == 0.0

    def test_cached_call_log(self):
        """Should mark cached calls."""
        log_entry = AICallLogger.log_call(
            model="claude-haiku-4-5-20251001",
            task_type="analyze_food",
            response=None,
            latency_ms=5,  # Very fast = cached
            success=True,
            cached=True,
            user_id=42,
        )

        assert log_entry["cached"] is True
        assert log_entry["latency_ms"] == 5


class TestTimer:
    """Test latency measurement."""

    def test_timer_measures_elapsed_time(self):
        """Timer should measure elapsed time."""
        import time

        with TimerContext() as timer:
            time.sleep(0.1)  # Sleep 100ms

        assert timer.elapsed_ms >= 100
        assert timer.elapsed_ms < 200  # Allow some margin

    def test_timer_zero_time(self):
        """Timer without sleep should report ~0ms."""
        with TimerContext() as timer:
            pass

        assert timer.elapsed_ms >= 0
        assert timer.elapsed_ms < 50  # Should be very fast

    def test_timer_context_manager(self):
        """Timer should work as context manager."""
        timer = TimerContext()
        assert timer.start_time is None
        assert timer.elapsed_ms == 0

        with timer:
            assert timer.start_time is not None
            assert timer.elapsed_ms == 0

        # After exiting context, elapsed_ms should be set (may be 0 for very fast ops)
        assert isinstance(timer.elapsed_ms, float)
        assert timer.elapsed_ms >= 0
