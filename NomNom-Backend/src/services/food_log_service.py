from datetime import datetime, timedelta, date as date_type, timezone

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


async def list_logs_for_date(db: AsyncSession, user_id: int, date: date_type) -> list[FoodLog]:
    """Fetch all logs for a specific date (YYYY-MM-DD)."""
    day_start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)
    result = await db.execute(
        select(FoodLog)
        .where(
            FoodLog.user_id == user_id,
            FoodLog.logged_at >= day_start,
            FoodLog.logged_at < day_end,
        )
        .order_by(FoodLog.logged_at.asc())
    )
    return list(result.scalars().all())


async def list_calendar_summary(
    db: AsyncSession, user_id: int, start_date: date_type, end_date: date_type
) -> list[dict]:
    """Fetch per-day summary for a date range (for calendar badges)."""
    start_dt = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)
    end_dt = datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0, tzinfo=timezone.utc) + timedelta(days=1)

    result = await db.execute(
        select(FoodLog)
        .where(
            FoodLog.user_id == user_id,
            FoodLog.logged_at >= start_dt,
            FoodLog.logged_at < end_dt,
        )
        .order_by(FoodLog.logged_at.desc())
    )
    logs = result.scalars().all()

    # Group by date
    by_date = {}
    for log in logs:
        date_key = log.logged_at.date().isoformat()
        if date_key not in by_date:
            by_date[date_key] = {"date": date_key, "count": 0, "photo_paths": []}
        by_date[date_key]["count"] += 1
        if len(by_date[date_key]["photo_paths"]) < 3:
            by_date[date_key]["photo_paths"].append(log.photo_path)

    return sorted(by_date.values(), key=lambda x: x["date"], reverse=True)


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
