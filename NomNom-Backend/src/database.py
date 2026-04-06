from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Register pgvector with asyncpg for vector column support
@event.listens_for(engine.sync_engine, "connect")
def _register_pgvector(dbapi_conn, connection_record):
    """Register pgvector type with asyncpg on connection."""
    try:
        import pgvector.asyncpg

        pgvector.asyncpg.register_vector(dbapi_conn)
    except ImportError:
        # pgvector not installed, skip
        pass
    except Exception:
        # Connection is not asyncpg (e.g., in tests), skip
        pass


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
