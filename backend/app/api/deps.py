from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
