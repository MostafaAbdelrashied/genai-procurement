from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ChatOutput(BaseResponse):
    response: str = Field(..., description="The assistant's response message")
    form: Dict[str, Any] = Field(..., description="The updated form schema")


class SessionDataOutput(BaseResponse):
    session_id: UUID = Field(..., description="The unique identifier for the session")
    form_data: Dict[str, Any] = Field(
        ..., description="The form data associated with the session"
    )
    created_at: datetime = Field(
        ..., description="The timestamp when the session was created"
    )
    last_updated_at: datetime = Field(
        ..., description="The timestamp when the session was last updated"
    )


class MessageDataOutput(BaseResponse):
    message_id: UUID = Field(..., description="The unique identifier for the message")
    session_id: UUID = Field(..., description="The unique identifier for the session")
    prompt: str = Field(..., description="The prompt message")
    response: str = Field(..., description="The response message")
    created_at: datetime = Field(
        ..., description="The timestamp when the message was created"
    )


class EmbeddingDataOutput(BaseResponse):
    embedding_id: UUID = Field(
        ..., description="The unique identifier for the embedding"
    )
    content: str = Field(..., description="The content associated with the embedding")
    embedding: list = Field(..., description="The embedding vector")
    properties: Dict[str, Any] = Field(
        ..., description="Additional properties associated with the embedding"
    )
    created_at: datetime = Field(
        ..., description="The timestamp when the embedding was created"
    )
    last_updated_at: datetime = Field(
        ..., description="The timestamp when the embedding was last updated"
    )


class EmbeddingWithDistanceOutput(EmbeddingDataOutput):
    distance: float = Field(
        ..., description="The distance between the query and the embedding"
    )


class UUIDOutput(BaseResponse):
    uuid: UUID = Field(..., description="The converted UUID")
