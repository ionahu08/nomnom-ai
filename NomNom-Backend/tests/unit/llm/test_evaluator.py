"""
Tests for AI accuracy evaluation.
"""

import pytest

from src.llm.evaluator import EvaluationMetrics, Evaluator


class TestEvaluationMetrics:
    """Test evaluation metrics tracking."""

    def test_initial_metrics(self):
        """Initial metrics should be zero."""
        metrics = EvaluationMetrics()
        assert metrics.total_analyses == 0
        assert metrics.total_corrections == 0
        assert metrics.accuracy_rate == 1.0

    def test_record_analysis(self):
        """Recording analysis should increment count."""
        metrics = EvaluationMetrics()
        metrics.record_analysis()
        assert metrics.total_analyses == 1

    def test_record_correction(self):
        """Recording correction should increment count."""
        metrics = EvaluationMetrics()
        metrics.record_correction("Pizza", "Pepperoni Pizza")
        assert metrics.total_corrections == 1

    def test_accuracy_rate_calculation(self):
        """Accuracy rate should be (total - corrections) / total."""
        metrics = EvaluationMetrics()
        # 100 analyses, 10 corrections = 90% accuracy
        for _ in range(100):
            metrics.record_analysis()
        for _ in range(10):
            metrics.record_correction("Food", "Corrected Food")

        assert metrics.accuracy_rate == 0.9

    def test_accuracy_rate_perfect(self):
        """Perfect accuracy when no corrections."""
        metrics = EvaluationMetrics()
        for _ in range(100):
            metrics.record_analysis()

        assert metrics.accuracy_rate == 1.0

    def test_accuracy_rate_no_analyses(self):
        """No analyses should return 100% accuracy."""
        metrics = EvaluationMetrics()
        assert metrics.accuracy_rate == 1.0

    def test_metrics_string_representation(self):
        """Metrics should have readable string representation."""
        metrics = EvaluationMetrics()
        metrics.record_analysis()
        metrics.record_analysis()
        metrics.record_correction("Food", "Other")
        metrics_str = str(metrics)
        assert "accuracy" in metrics_str
        assert "corrections" in metrics_str


class TestEvaluator:
    """Test accuracy evaluator."""

    @pytest.mark.asyncio
    async def test_record_correction_doesnt_crash(self):
        """Recording correction should not raise errors."""
        await Evaluator.record_correction(
            user_id=1,
            food_log_id=123,
            original_food_name="Pizza",
            corrected_food_name="Pepperoni Pizza",
            model_used="claude-haiku-4-5-20251001",
        )

    @pytest.mark.asyncio
    async def test_get_accuracy_rate_returns_float(self):
        """Get accuracy rate should return a float."""
        rate = await Evaluator.get_accuracy_rate(model="claude-haiku-4-5-20251001")
        assert isinstance(rate, float)
        assert 0 <= rate <= 1

    @pytest.mark.asyncio
    async def test_get_accuracy_for_specific_user(self):
        """Get accuracy with user filter."""
        rate = await Evaluator.get_accuracy_rate(user_id=42)
        assert isinstance(rate, float)

    @pytest.mark.asyncio
    async def test_get_accuracy_with_date_range(self):
        """Get accuracy with date range."""
        rate = await Evaluator.get_accuracy_rate(days=7)
        assert isinstance(rate, float)

    def test_evaluation_context_excellent(self):
        """<2% correction rate is excellent."""
        context = Evaluator.get_evaluation_context(0.01)
        assert "Excellent" in context
        assert "98%" in context

    def test_evaluation_context_good(self):
        """2-5% correction rate is good."""
        context = Evaluator.get_evaluation_context(0.03)
        assert "Good" in context
        assert "95" in context or "98" in context

    def test_evaluation_context_fair(self):
        """5-10% correction rate is fair."""
        context = Evaluator.get_evaluation_context(0.07)
        assert "Fair" in context
        assert "90" in context or "95" in context

    def test_evaluation_context_poor(self):
        """>10% correction rate is poor."""
        context = Evaluator.get_evaluation_context(0.15)
        assert "Poor" in context
        assert "90%" in context
