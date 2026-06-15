"""Test analytics repository and API."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from src.models.food_log import FoodLog
from src.models.user import User, UserProfile
from src.repositories.analytics_repository import AnalyticsRepository


@pytest.fixture
def user_with_profile(db: Session):
    """Create a test user with profile."""
    user = User(email="test@example.com", hashed_password="hashed")
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        age=30,
        gender="male",
        height_cm=180,
        weight_kg=80,
        activity_level="moderate",
        calorie_target=2000,
        protein_target=150,
        carb_target=200,
        fat_target=65,
    )
    db.add(profile)
    db.commit()

    return user, profile


@pytest.fixture
def food_logs(db: Session, user_with_profile):
    """Create test food logs."""
    user, _ = user_with_profile
    now = datetime.now(timezone.utc)

    logs = [
        FoodLog(
            user_id=user.id,
            photo_path="/test/food1.jpg",
            food_name="Chicken Breast",
            calories=250,
            protein_g=35,
            carbs_g=0,
            fat_g=5,
            cat_roast="Looking good!",
            logged_at=now - timedelta(days=6),
        ),
        FoodLog(
            user_id=user.id,
            photo_path="/test/food2.jpg",
            food_name="Noodles",
            calories=400,
            protein_g=10,
            carbs_g=60,
            fat_g=15,
            cat_roast="Carbs carbs carbs...",
            logged_at=now - timedelta(days=5),
        ),
        FoodLog(
            user_id=user.id,
            photo_path="/test/food3.jpg",
            food_name="Noodles",
            calories=400,
            protein_g=10,
            carbs_g=60,
            fat_g=15,
            cat_roast="Again?",
            logged_at=now - timedelta(days=4),
        ),
        FoodLog(
            user_id=user.id,
            photo_path="/test/food4.jpg",
            food_name="Chicken Breast",
            calories=250,
            protein_g=35,
            carbs_g=0,
            fat_g=5,
            cat_roast="Nice!",
            logged_at=now - timedelta(days=3),
        ),
        FoodLog(
            user_id=user.id,
            photo_path="/test/food5.jpg",
            food_name="Broccoli",
            calories=50,
            protein_g=4,
            carbs_g=8,
            fat_g=0.5,
            cat_roast="Veggies!",
            logged_at=now - timedelta(days=2),
        ),
        FoodLog(
            user_id=user.id,
            photo_path="/test/food6.jpg",
            food_name="Noodles",
            calories=400,
            protein_g=10,
            carbs_g=60,
            fat_g=15,
            cat_roast="You again?",
            logged_at=now - timedelta(days=1),
        ),
    ]

    db.add_all(logs)
    db.commit()

    return logs


def test_get_food_logs_for_period(db: Session, food_logs):
    """Test fetching food logs for a period."""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=7)
    end_date = now

    logs = AnalyticsRepository.get_food_logs_for_period(db, food_logs[0].user_id, start_date, end_date)

    assert len(logs) == 6


def test_get_aggregated_stats(db: Session, food_logs, user_with_profile):
    """Test aggregating nutrition statistics."""
    user, _ = user_with_profile
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=7)
    end_date = now

    stats = AnalyticsRepository.get_aggregated_stats(db, user.id, start_date, end_date)

    # Verify totals
    assert stats["calories"]["total"] == 1750  # 250+400+400+250+50+400
    assert stats["protein_g"]["total"] == 104  # 35+10+10+35+4+10
    assert stats["carbs_g"]["total"] == 188  # 0+60+60+0+8+60
    assert stats["fat_g"]["total"] == 55.5  # 5+15+15+5+0.5+15

    # Verify averages
    assert stats["calories"]["average"] == 291.7  # 1750 / 6
    assert stats["protein_g"]["average"] == 17.3  # 104 / 6
    assert stats["carbs_g"]["average"] == 31.3  # 188 / 6
    assert stats["fat_g"]["average"] == 9.3  # 55.5 / 6

    # Verify top foods
    assert len(stats["top_foods"]) > 0
    assert stats["top_foods"][0]["food"] == "Noodles"
    assert stats["top_foods"][0]["count"] == 3


def test_get_days_logged(db: Session, food_logs, user_with_profile):
    """Test calculating days logged."""
    user, _ = user_with_profile
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=7)
    end_date = now

    days_logged, total_days = AnalyticsRepository.get_days_logged(db, user.id, start_date, end_date)

    assert days_logged == 6
    assert total_days == 7


def test_get_user_targets(db: Session, user_with_profile):
    """Test fetching user targets."""
    user, profile = user_with_profile

    targets = AnalyticsRepository.get_user_targets(db, user.id)

    assert targets["calorie_target"] == 2000
    assert targets["protein_target"] == 150
    assert targets["carb_target"] == 200
    assert targets["fat_target"] == 65


def test_get_user_targets_default(db: Session):
    """Test default targets for user without profile."""
    user = User(email="noprofile@example.com", hashed_password="hashed")
    db.add(user)
    db.commit()

    targets = AnalyticsRepository.get_user_targets(db, user.id)

    assert targets["calorie_target"] == 2000
    assert targets["protein_target"] == 150
    assert targets["carb_target"] == 200
    assert targets["fat_target"] == 65
