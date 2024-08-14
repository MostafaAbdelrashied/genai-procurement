from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from loguru import logger

from form.db.db_check import DatabaseChecks, get_db_checks
from form.db.db_tables import Message, Session
from form.models.exceptions import DatabaseOperationError

router = APIRouter()


@router.get("/check_health", description="Health check", response_class=Response)
async def health_check():
    return Response(status_code=200, content="OK", media_type="text/plain")


@router.get("/check_db", description="Check DB connection")
async def check_db(db_checks: DatabaseChecks = Depends(get_db_checks)):
    try:
        await db_checks.execute_query("SELECT 1")
        return Response(status_code=200, content="OK", media_type="text/plain")
    except DatabaseOperationError as e:
        logger.error(f"Database error while checking connection: {e}")
        raise HTTPException(
            status_code=500, detail="Could not connect to the database."
        )


@router.get(
    "/check_table/{table_name}", description="Check if a table exists in the database"
)
async def check_table(
    table_name: str, db_checks: DatabaseChecks = Depends(get_db_checks)
):
    try:
        if await db_checks.check_table_exists(table_name):
            return Response(
                status_code=200, content=f"Table {table_name} exists in the database."
            )
        raise HTTPException(
            status_code=404,
            detail=f"Table {table_name} does not exist in the database.",
        )
    except DatabaseOperationError as e:
        logger.error(f"Database error while checking table {table_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/check_tables", description="Check if tables exist in the database")
async def check_tables(db_checks: DatabaseChecks = Depends(get_db_checks)):
    tables_to_check = [Message.__table__, Session.__table__]
    missing_tables: List[str] = []

    try:
        for table in tables_to_check:
            if not await db_checks.check_table_exists(table):
                missing_tables.append(table)

        if not missing_tables:
            return Response(
                status_code=200, content="All tables exist in the database."
            )
        raise HTTPException(
            status_code=404,
            detail=f"Tables {missing_tables} do not exist in the database.",
        )
    except DatabaseOperationError as e:
        logger.error(f"Database error while checking tables: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
