import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_food_photo(client: AsyncClient, auth_headers: dict):
    """Test the analyze endpoint returns a stub response."""
    # Create a fake image file
    files = {"file": ("test.jpg", b"fake-image-data", "image/jpeg")}
    resp = await client.post(
        "/api/v1/food-logs/analyze",
        files=files,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "food_name" in data
    assert "calories" in data
    assert "cat_roast" in data


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
