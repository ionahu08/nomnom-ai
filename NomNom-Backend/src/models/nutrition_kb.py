"""
NutritionKB — Knowledge base for RAG-powered meal recommendations.

Stores nutrition tips, food facts, and dietary guidance as embeddings.
RAG queries semantic similarity to find relevant entries.
"""

from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.llm.embedding import EMBEDDING_DIM


class NutritionKB(Base):
    """Nutrition knowledge base entry."""

    __tablename__ = "nutrition_kb"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<NutritionKB(id={self.id}, title={self.title}, category={self.category})>"
