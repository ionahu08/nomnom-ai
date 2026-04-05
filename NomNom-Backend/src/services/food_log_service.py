from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.food_log import FoodLog
from src.schemas.food_log import FoodLogCreate


async def create_food_log(db: AsyncSession, user_id: int, data: FoodLogCreate) -> FoodLog:
    food_log = FoodLog(user_id=user_id, **data.model_dump())
    db.add(food_log)
    await db.commit()
    await db.refresh(food_log)
    return food_log


async def list_today_logs(db: AsyncSession, user_id: int) -> list[FoodLog]:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(FoodLog)
        .where(FoodLog.user_id == user_id, FoodLog.logged_at >= today_start)
        .order_by(FoodLog.logged_at.desc())
    )
    return list(result.scalars().all())


async def get_food_log(db: AsyncSession, user_id: int, log_id: int) -> FoodLog | None:
    result = await db.execute(
        select(FoodLog).where(FoodLog.id == log_id, FoodLog.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete_food_log(db: AsyncSession, user_id: int, log_id: int) -> bool:
    food_log = await get_food_log(db, user_id, log_id)
    if food_log is None:
        return False
    await db.delete(food_log)
    await db.commit()
    return True
