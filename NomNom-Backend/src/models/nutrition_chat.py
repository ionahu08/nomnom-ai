from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship, Mapped
import uuid
from src.database import Base


class NutritionChatMessage(Base):
    __tablename__ = "nutrition_chat_messages"

    id: Mapped[str] = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = Column(String(20), nullable=False)  # "user" or "assistant"
    content: Mapped[str] = Column(Text, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Composite index for fast retrieval of user messages ordered by time
    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
    )
