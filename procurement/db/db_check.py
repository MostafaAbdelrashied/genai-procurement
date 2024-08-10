from fastapi import Depends
from loguru import logger
from procurement.api.deps import get_session
from procurement.models.exceptions import DatabaseOperationError
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseChecks:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def execute_query(self, query: str) -> bool:
        try:
            await self.db_session.execute(text(query))
            return True
        except ProgrammingError as _:
            return False
        except Exception as e:
            logger.exception(f"Error executing query: {e}")
            raise DatabaseOperationError(f"Error executing query: {str(e)}")

    async def check_table_exists(self, table_name: str) -> bool:
        return await self.execute_query(f"SELECT 1 FROM {table_name} LIMIT 1")


async def get_db_checks(
    db_session: AsyncSession = Depends(get_session),
) -> DatabaseChecks:
    return DatabaseChecks(db_session)
