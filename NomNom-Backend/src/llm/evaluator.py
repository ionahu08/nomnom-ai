"""
Evaluator — Track user corrections to measure AI accuracy.

When a user edits a food log after AI analysis, it's a signal:
- AI got something wrong
- User corrected it
- We should track this for model evaluation

Metrics:
- How often does AI get food identification wrong?
- Which models perform better?
- Are certain food types harder?

In production, this would:
1. Flag food_logs with is_user_corrected=True
2. Compare original AI output vs user's corrections
3. Generate accuracy metrics per model/food type
4. Feed back to model selection (downgrade bad models)

For now, we provide the tracking interface.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class EvaluationMetrics:
    """Track evaluation metrics."""

    def __init__(self):
        """Initialize metrics."""
        self.total_corrections = 0
        self.total_analyses = 0

    def record_analysis(self) -> None:
        """Record a food analysis."""
        self.total_analyses += 1

    def record_correction(self, original_food_name: str, corrected_food_name: str) -> None:
        """
        Record a user correction.

        Args:
            original_food_name: What AI said
            corrected_food_name: What user corrected to
        """
        self.total_corrections += 1
        logger.info(
            f"Correction recorded: '{original_food_name}' → '{corrected_food_name}'"
        )

    @property
    def accuracy_rate(self) -> float:
        """Get accuracy rate (0-1)."""
        if self.total_analyses == 0:
            return 1.0
        return 1.0 - (self.total_corrections / self.total_analyses)

    def __str__(self) -> str:
        """String representation."""
        return f"EvaluationMetrics(accuracy={self.accuracy_rate:.2%}, corrections={self.total_corrections}/{self.total_analyses})"


class Evaluator:
    """Evaluate AI accuracy from user corrections."""

    @staticmethod
    async def record_correction(
        user_id: int,
        food_log_id: int,
        original_food_name: str,
        corrected_food_name: str,
        model_used: str,
    ) -> None:
        """
        Record a correction made by the user.

        Args:
            user_id: User who made the correction
            food_log_id: Food log that was corrected
            original_food_name: Original AI analysis
            corrected_food_name: User's correction
            model_used: Model that made the original analysis

        Note:
        In production, this would:
        1. Flag food_logs.is_user_corrected = True
        2. Store correction details in a corrections table
        3. Track per model/user/food type
        4. Generate accuracy reports

        For now, this just logs the correction.
        """
        logger.info(
            f"Correction recorded for food_log {food_log_id}",
            extra={
                "user_id": user_id,
                "original": original_food_name,
                "corrected": corrected_food_name,
                "model": model_used,
            },
        )

    @staticmethod
    async def get_accuracy_rate(
        model: Optional[str] = None,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> float:
        """
        Get accuracy rate for a model or user.

        Args:
            model: Model name (optional)
            user_id: User ID (optional)
            days: Look back window in days

        Returns:
            Accuracy rate (0-1)

        Note:
        In production, this would:
        1. Query food_logs for is_user_corrected=True
        2. Filter by model/user/date range
        3. Calculate: 1 - (corrections / total_analyses)

        For now, returns 1.0 (perfect accuracy).
        """
        # TODO: Implement with database query
        # SELECT
        #   COUNT(CASE WHEN is_user_corrected THEN 1 END) as corrections,
        #   COUNT(*) as total
        # FROM food_logs
        # WHERE created_at > NOW() - INTERVAL days
        #   AND (model = ? OR ? IS NULL)
        #   AND (user_id = ? OR ? IS NULL)
        return 1.0

    @staticmethod
    def get_evaluation_context(
        correction_rate: float,
    ) -> str:
        """Get readable context for accuracy."""
        if correction_rate < 0.02:
            return "Excellent (>98% accurate)"
        elif correction_rate < 0.05:
            return "Good (95-98% accurate)"
        elif correction_rate < 0.10:
            return "Fair (90-95% accurate)"
        else:
            return "Poor (<90% accurate)"


# Global evaluation metrics instance
eval_metrics = EvaluationMetrics()
