import json
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from loguru import logger
from procurement.db.db_operations import DatabaseOperations, get_db_ops
from procurement.models.exceptions import DatabaseOperationError
from procurement.models.responses import MessageDataOutput, SessionDataOutput
from procurement.utils.form_handler import read_json

router = APIRouter()


@router.post(
    "/create_session",
    response_model=SessionDataOutput,
    description="Create a new session in the database",
)
async def create_session(
    session_id: UUID,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> SessionDataOutput:
    try:
        await db_ops.create_session(
            session_id, json.dumps(read_json(path="procurement/schemas/form.json"))
        )
        session_data = await db_ops.get_session_data(session_id)
        return SessionDataOutput(
            session_id=session_data.session_id,
            form_data=json.loads(session_data.form_data),
            created_at=session_data.created_at,
            last_updated_at=session_data.last_updated_at,
        )
    except DatabaseOperationError as e:
        logger.error(f"Database error while creating session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_all_sessions",
    response_model=List[SessionDataOutput],
    description="Get all available sessions from the database",
)
async def get_all_sessions(
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> List[SessionDataOutput]:
    try:
        sessions = await db_ops.get_all_sessions()
        return [
            SessionDataOutput(
                session_id=session.session_id,
                form_data=json.loads(session.form_data),
                created_at=session.created_at,
                last_updated_at=session.last_updated_at,
            )
            for session in sessions
        ]
    except DatabaseOperationError as e:
        logger.error(f"Database error while fetching all sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_session_data/{session_id}",
    response_model=SessionDataOutput,
    description="Get session data from the database",
)
async def get_session(
    session_id: UUID,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> SessionDataOutput:
    try:
        session_data = await db_ops.get_session_data(session_id)
        if not session_data:
            raise HTTPException(
                status_code=404, detail=f"Session {session_id} does not exist"
            )
        return SessionDataOutput(
            session_id=session_data.session_id,
            form_data=json.loads(session_data.form_data),
            created_at=session_data.created_at,
            last_updated_at=session_data.last_updated_at,
        )
    except DatabaseOperationError as e:
        logger.error(f"Database error while fetching session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_messages_history/{session_id}",
    response_model=List[MessageDataOutput],
    description="Get all messages for a session from the database",
)
async def get_session_messages(
    session_id: UUID,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> List[MessageDataOutput]:
    try:
        messages = await db_ops.get_messages_for_session(session_id)
        return [
            MessageDataOutput(
                message_id=message.message_id,
                session_id=message.session_id,
                prompt=message.prompt,
                response=message.response,
                created_at=message.created_at,
            )
            for message in messages
        ]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseOperationError as e:
        logger.error(
            f"Database error while fetching messages for session {session_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/update_session_form/{session_id}",
    response_model=SessionDataOutput,
    description="Update session data in the database",
)
async def update_session(
    session_id: UUID,
    form_data: dict,
    db_ops: DatabaseOperations = Depends(get_db_ops),
    create_if_not_exists: bool = False,
) -> SessionDataOutput:
    try:
        if create_if_not_exists:
            await db_ops.upsert_session(
                session_id=session_id, form_data=json.dumps(form_data)
            )
        await db_ops.update_session_data(session_id, json.dumps(form_data))
        updated_session = await db_ops.get_session_data(session_id)

        return SessionDataOutput(
            session_id=updated_session.session_id,
            form_data=json.loads(updated_session.form_data),
            created_at=updated_session.created_at,
            last_updated_at=updated_session.last_updated_at,
        )
    except ValueError as _:
        raise HTTPException(
            status_code=404, detail=f"Session {session_id} does not exist"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database error while updating session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/delete_session/{session_id}",
    status_code=204,
    description="Delete a session from the database",
)
async def delete_session(
    session_id: UUID,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> Response:
    try:
        await db_ops.delete_session(session_id)
        return Response(status_code=204)
    except ValueError as _:
        raise HTTPException(
            status_code=404, detail=f"Session {session_id} does not exist"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database error while deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
