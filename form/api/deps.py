from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from form.db import get_async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session() as session:
        yield session
