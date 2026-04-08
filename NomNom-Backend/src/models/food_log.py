from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.llm.embedding import EMBEDDING_DIM


class FoodLog(Base):
    __tablename__ = "food_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Photo
    photo_path: Mapped[str] = mapped_column(String(500))

    # AI-detected food data
    food_name: Mapped[str] = mapped_column(String(200))
    calories: Mapped[int] = mapped_column(Integer)
    protein_g: Mapped[float] = mapped_column(Float)
    carbs_g: Mapped[float] = mapped_column(Float)
    fat_g: Mapped[float] = mapped_column(Float)
    food_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cuisine_origin: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Cat roast
    cat_roast: Mapped[str] = mapped_column(Text)

    # Meal type (breakfast, lunch, dinner, snack)
    meal_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Raw AI response for debugging
    ai_raw_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Embedding vector for semantic cache and search
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )

    # User corrections (for future evaluation tracking)
    is_user_corrected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()
