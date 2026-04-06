"""
Seed Script — Populate nutrition knowledge base.

Run this once at deployment to populate the nutrition KB:
  python -m src.llm.seed_knowledge
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.services.knowledge_service import seed_nutrition_kb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Seed the nutrition knowledge base."""
    logger.info("Connecting to database...")

    # Create async engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        logger.info("Starting knowledge base seeding...")
        inserted = await seed_nutrition_kb(db)
        logger.info(f"Seeding complete. Inserted {inserted} entries.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
