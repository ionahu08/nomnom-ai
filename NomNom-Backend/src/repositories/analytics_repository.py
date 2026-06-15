from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.models.food_log import FoodLog
from src.models.user import User, UserProfile


class AnalyticsRepository:
    """Repository for fetching and aggregating food log analytics."""

    @staticmethod
    def get_food_logs_for_period(
        db: Session, user_id: int, start_date: datetime, end_date: datetime
    ) -> list[FoodLog]:
        """Fetch all food logs for a user within a date range."""
        return db.query(FoodLog).filter(
            and_(
                FoodLog.user_id == user_id,
                FoodLog.logged_at >= start_date,
                FoodLog.logged_at < end_date,
            )
        ).all()

    @staticmethod
    def get_aggregated_stats(
        db: Session, user_id: int, start_date: datetime, end_date: datetime
    ) -> dict:
        """Calculate aggregated nutrition statistics for a date range."""
        logs = AnalyticsRepository.get_food_logs_for_period(db, user_id, start_date, end_date)

        if not logs:
            return {
                "total_logs": 0,
                "calories": {"total": 0, "average": 0},
                "protein_g": {"total": 0, "average": 0},
                "carbs_g": {"total": 0, "average": 0},
                "fat_g": {"total": 0, "average": 0},
                "daily_breakdown": [],
                "top_foods": [],
            }

        # Calculate totals
        total_calories = sum(log.calories for log in logs)
        total_protein = sum(log.protein_g for log in logs)
        total_carbs = sum(log.carbs_g for log in logs)
        total_fat = sum(log.fat_g for log in logs)

        # Calculate averages
        num_logs = len(logs)
        avg_calories = total_calories / num_logs if num_logs > 0 else 0
        avg_protein = total_protein / num_logs if num_logs > 0 else 0
        avg_carbs = total_carbs / num_logs if num_logs > 0 else 0
        avg_fat = total_fat / num_logs if num_logs > 0 else 0

        # Daily breakdown
        daily_data = {}
        for log in logs:
            date_key = log.logged_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "calories": 0,
                    "protein_g": 0,
                    "carbs_g": 0,
                    "fat_g": 0,
                }
            daily_data[date_key]["calories"] += log.calories
            daily_data[date_key]["protein_g"] += log.protein_g
            daily_data[date_key]["carbs_g"] += log.carbs_g
            daily_data[date_key]["fat_g"] += log.fat_g

        daily_breakdown = sorted(daily_data.values(), key=lambda x: x["date"])

        # Top foods
        food_counts = {}
        food_calories = {}
        for log in logs:
            if log.food_name not in food_counts:
                food_counts[log.food_name] = 0
                food_calories[log.food_name] = 0
            food_counts[log.food_name] += 1
            food_calories[log.food_name] += log.calories

        top_foods = sorted(
            [
                {"food": name, "count": food_counts[name], "calories": food_calories[name]}
                for name in food_counts.keys()
            ],
            key=lambda x: x["count"],
            reverse=True,
        )[:5]

        return {
            "total_logs": num_logs,
            "calories": {"total": int(total_calories), "average": round(avg_calories, 1)},
            "protein_g": {"total": round(total_protein, 1), "average": round(avg_protein, 1)},
            "carbs_g": {"total": round(total_carbs, 1), "average": round(avg_carbs, 1)},
            "fat_g": {"total": round(total_fat, 1), "average": round(avg_fat, 1)},
            "daily_breakdown": daily_breakdown,
            "top_foods": top_foods,
        }

    @staticmethod
    def get_days_logged(
        db: Session, user_id: int, start_date: datetime, end_date: datetime
    ) -> tuple[int, int]:
        """Get number of days with logs and total days in period."""
        logs = AnalyticsRepository.get_food_logs_for_period(db, user_id, start_date, end_date)

        if not logs:
            return 0, (end_date - start_date).days

        unique_dates = set(log.logged_at.date() for log in logs)
        days_logged = len(unique_dates)

        total_days = (end_date - start_date).days

        return days_logged, total_days

    @staticmethod
    def get_user_targets(db: Session, user_id: int) -> dict:
        """Get user's nutrition targets from profile."""
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if not profile:
            # Default targets
            return {
                "calorie_target": 2000,
                "protein_target": 150,
                "carb_target": 200,
                "fat_target": 65,
            }

        return {
            "calorie_target": profile.calorie_target or 2000,
            "protein_target": profile.protein_target or 150,
            "carb_target": profile.carb_target or 200,
            "fat_target": profile.fat_target or 65,
        }
