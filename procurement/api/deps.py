from collections.abc import AsyncGenerator

from procurement.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session() as session:
        yield session
