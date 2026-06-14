import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import Base, get_db
from src.app import app

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True)
async def setup_db():
    """Create fresh database for each test."""
    # Create new engine per test to ensure isolation
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client():
    """Async HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client: AsyncClient) -> str:
    """Register a test user and return the JWT token."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "test1234"},
    )
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}
