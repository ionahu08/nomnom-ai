"""
Seed Script — Populate nutrition knowledge base.

Run this once at deployment to populate the nutrition KB:
  python -m src.llm.seed_knowledge

Or with --refresh flag to clear and reseed:
  python -m src.llm.seed_knowledge --refresh
"""

import argparse
import asyncio
import logging
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.services.knowledge_service import seed_nutrition_kb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def main(refresh: bool = False):
    """
    Seed the nutrition knowledge base.

    Args:
        refresh: If True, delete existing KB and reseed from scratch
    """
    try:
        logger.info("Connecting to database...")

        # Create async engine and session
        engine = create_async_engine(settings.database_url, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as db:
            if refresh:
                logger.info("Clearing existing knowledge base...")
                try:
                    await db.execute(text("DELETE FROM nutrition_chunks"))
                    await db.commit()
                    logger.info("Knowledge base cleared.")
                except Exception as e:
                    logger.warning(f"Could not clear KB (table may not exist): {e}")

            logger.info("Starting knowledge base seeding...")
            inserted = await seed_nutrition_kb(db)
            logger.info(f"✅ Seeding complete. Inserted {inserted} entries.")

        await engine.dispose()
        return 0

    except Exception as e:
        logger.error(f"❌ Failed to seed knowledge base: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed nutrition knowledge base")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Delete existing KB and reseed from scratch",
    )
    args = parser.parse_args()

    exit_code = asyncio.run(main(refresh=args.refresh))
    sys.exit(exit_code)
