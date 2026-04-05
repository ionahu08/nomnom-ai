import pytest
from httpx import AsyncClient

PROFILE_DATA = {
    "age": 25,
    "gender": "female",
    "height_cm": 165,
    "weight_kg": 60,
    "activity_level": "moderate",
    "cat_style": "sassy",
    "allergies": ["peanuts"],
    "dietary_restrictions": ["vegetarian"],
    "cuisine_preferences": ["japanese", "mexican"],
}


@pytest.mark.asyncio
async def test_create_profile(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/profile/", json=PROFILE_DATA, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["age"] == 25
    assert data["cat_style"] == "sassy"
    assert data["allergies"] == ["peanuts"]
    # Check auto-calculated targets
    assert data["targets"]["calorie_target"] == 2085
    assert data["targets"]["protein_target"] > 0
    assert data["targets"]["carb_target"] > 0
    assert data["targets"]["fat_target"] > 0


@pytest.mark.asyncio
async def test_create_profile_duplicate(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/profile/", json=PROFILE_DATA, headers=auth_headers)
    resp = await client.post("/api/v1/profile/", json=PROFILE_DATA, headers=auth_headers)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/profile/", json=PROFILE_DATA, headers=auth_headers)
    resp = await client.get("/api/v1/profile/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["gender"] == "female"


@pytest.mark.asyncio
async def test_get_profile_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/profile/", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/profile/", json=PROFILE_DATA, headers=auth_headers)
    resp = await client.patch(
        "/api/v1/profile/",
        json={"cat_style": "grumpy", "weight_kg": 65},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["cat_style"] == "grumpy"
    assert data["weight_kg"] == 65.0
    # Age should be unchanged
    assert data["age"] == 25


@pytest.mark.asyncio
async def test_profile_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/profile/")
    assert resp.status_code == 401
