from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)

    # Body stats
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(20))
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    activity_level: Mapped[str] = mapped_column(String(20))

    # Cat personality
    cat_style: Mapped[str] = mapped_column(String(50), default="sassy")

    # Dietary info (stored as JSON lists)
    allergies: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dietary_restrictions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cuisine_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Daily targets (nullable = auto-calculated from TDEE)
    calorie_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protein_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carb_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fat_target: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Preferences
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="profile")
