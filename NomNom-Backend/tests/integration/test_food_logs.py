from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from src.schemas.food_log import FoodAnalysisResponse

MOCK_ANALYSIS = FoodAnalysisResponse(
    food_name="Test Burger",
    calories=500,
    protein_g=30.0,
    carbs_g=40.0,
    fat_g=25.0,
    food_category="fast food",
    cuisine_origin="American",
    cat_roast="A burger? How original.",
)


@pytest.mark.asyncio
async def test_analyze_food_photo(client: AsyncClient, auth_headers: dict):
    """Test the analyze endpoint with mocked AI."""
    with patch("src.api.food_logs.ai_analyze", new_callable=AsyncMock, return_value=MOCK_ANALYSIS):
        files = {"file": ("test.jpg", b"fake-image-data", "image/jpeg")}
        resp = await client.post(
            "/api/v1/food-logs/analyze",
            files=files,
            headers=auth_headers,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["food_name"] == "Test Burger"
    assert data["calories"] == 500
    assert data["cat_roast"] == "A burger? How original."


@pytest.mark.asyncio
async def test_save_food_log(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/food-logs/",
        json={
            "photo_path": "test123.jpg",
            "food_name": "Chicken Salad",
            "calories": 350,
            "protein_g": 30.0,
            "carbs_g": 20.0,
            "fat_g": 15.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "A salad? Who are you trying to impress?",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["food_name"] == "Chicken Salad"
    assert data["calories"] == 350
    assert data["cat_roast"] == "A salad? Who are you trying to impress?"


@pytest.mark.asyncio
async def test_list_today_logs(client: AsyncClient, auth_headers: dict):
    # Save two food logs
    for food in ["Pizza", "Burger"]:
        await client.post(
            "/api/v1/food-logs/",
            json={
                "photo_path": f"{food.lower()}.jpg",
                "food_name": food,
                "calories": 500,
                "protein_g": 20.0,
                "carbs_g": 50.0,
                "fat_g": 25.0,
                "cat_roast": f"Really? {food}?",
            },
            headers=auth_headers,
        )

    resp = await client.get("/api/v1/food-logs/today", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delete_food_log(client: AsyncClient, auth_headers: dict):
    # Save a food log
    resp = await client.post(
        "/api/v1/food-logs/",
        json={
            "photo_path": "delete_me.jpg",
            "food_name": "Donut",
            "calories": 300,
            "protein_g": 5.0,
            "carbs_g": 40.0,
            "fat_g": 15.0,
            "cat_roast": "This one's getting deleted, just like your diet plan.",
        },
        headers=auth_headers,
    )
    log_id = resp.json()["id"]

    # Delete it
    resp = await client.delete(f"/api/v1/food-logs/{log_id}", headers=auth_headers)
    assert resp.status_code == 204

    # Verify it's gone
    resp = await client.get("/api/v1/food-logs/today", headers=auth_headers)
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent_log(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/v1/food-logs/999", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_food_logs_require_auth(client: AsyncClient):
    resp = await client.get("/api/v1/food-logs/today")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_logs_by_date(client: AsyncClient, auth_headers: dict):
    """Test fetching logs for a specific date."""
    # Save a food log
    resp = await client.post(
        "/api/v1/food-logs/",
        json={
            "photo_path": "sushi.jpg",
            "food_name": "Sushi",
            "calories": 400,
            "protein_g": 25.0,
            "carbs_g": 45.0,
            "fat_g": 12.0,
            "cat_roast": "Raw fish? Fancy.",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201

    # Fetch logs for today using /by-date endpoint
    resp = await client.get("/api/v1/food-logs/by-date?date=2026-04-08", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["food_name"] == "Sushi"
    assert data[0]["calories"] == 400


@pytest.mark.asyncio
async def test_get_logs_by_date_invalid_format(client: AsyncClient, auth_headers: dict):
    """Test /by-date with invalid date format."""
    resp = await client.get("/api/v1/food-logs/by-date?date=04-08-2026", headers=auth_headers)
    assert resp.status_code == 400
    assert "Invalid date format" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_calendar_summary(client: AsyncClient, auth_headers: dict):
    """Test fetching calendar summary for a date range."""
    # Save food logs on different dates
    logs_data = [
        {"photo_path": "pizza.jpg", "food_name": "Pizza", "calories": 600},
        {"photo_path": "salad.jpg", "food_name": "Salad", "calories": 250},
    ]

    for log in logs_data:
        await client.post(
            "/api/v1/food-logs/",
            json={
                **log,
                "protein_g": 20.0,
                "carbs_g": 50.0,
                "fat_g": 15.0,
                "cat_roast": "Test roast",
            },
            headers=auth_headers,
        )

    # Fetch calendar summary
    resp = await client.get(
        "/api/v1/food-logs/calendar-summary?start=2026-04-01&end=2026-04-30",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    # Find today's summary
    today_summary = next((d for d in data if d["date"] == "2026-04-08"), None)
    assert today_summary is not None
    assert today_summary["count"] == 2
    assert len(today_summary["photo_paths"]) >= 1


@pytest.mark.asyncio
async def test_get_calendar_summary_invalid_dates(client: AsyncClient, auth_headers: dict):
    """Test calendar-summary with invalid date format."""
    resp = await client.get(
        "/api/v1/food-logs/calendar-summary?start=04-01-2026&end=04-30-2026",
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "Invalid date format" in resp.json()["detail"]
