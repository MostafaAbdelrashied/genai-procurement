import json
from datetime import datetime
from uuid import UUID, uuid5

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from procurement.agents.agents_manager import AgentsManager
from procurement.api.deps import get_session
from procurement.db.db_operations import DatabaseOperations
from procurement.models.exceptions import AgentProcessingError, DatabaseOperationError
from procurement.models.requests import ChatInput
from procurement.models.responses import ChatOutput
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/message",
    response_model=ChatOutput,
    description="Chat with GPT",
)
async def chat_with_gpt(
    input_data: ChatInput,
    session_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ChatOutput:
    agent_manager = AgentsManager(session, session_id)
    db_ops = DatabaseOperations(session)

    try:
        response = await agent_manager.process_input(input_prompt=input_data.message)
        chat_response = ChatOutput(
            response=response["content"], form=response["schema"]
        )
    except AgentProcessingError as e:
        logger.exception(f"Agent processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in chat_with_gpt: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again or contact the admin if the issue persists.",
        )

    try:
        await db_ops.upsert_session(
            session_id=session_id, form_data=json.dumps(chat_response.form)
        )
        await db_ops.upsert_message(
            message_id=uuid5(session_id, datetime.now().isoformat()),
            session_id=session_id,
            prompt=input_data.message,
            response=chat_response.response,
        )
    except DatabaseOperationError as e:
        logger.exception(f"Database operation error: {str(e)}")
        # We don't raise an exception here because we want to return the chat response
        # even if the database operation fails
        logger.warning("Failed to save chat history to database")

    return chat_response
