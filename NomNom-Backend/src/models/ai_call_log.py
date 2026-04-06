"""
AI Call Log model — Track every AI API call for observability.

Every time Claude is called, we log:
- Which model was used
- What task it was
- How many tokens (input + output)
- How long it took
- How much it cost
- Success/failure

This powers the /ai-stats endpoints.
"""

from datetime import datetime

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class AICallLog(Base):
    """Log entry for every AI API call."""

    __tablename__ = "ai_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Who triggered it
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Which model
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    # What task
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Token usage
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)

    # Performance
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    # Cost (estimated, in USD)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=False)

    # Success/failure
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Caching
    cached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )

    def __repr__(self) -> str:
        return f"<AICallLog(model={self.model}, task={self.task_type}, tokens={self.input_tokens}+{self.output_tokens}, cost=${self.estimated_cost:.4f})>"
