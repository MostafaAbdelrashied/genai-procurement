from pydantic import BaseModel, Field
from typing import Dict


class ChatInput(BaseModel):
    message: str = Field(..., min_length=1, description="The user's input message")


class Document(BaseModel):
    content: str = Field(..., min_length=1, description="The content to be embedded")
    properties: Dict[str, str | float | int | bool] = Field(
        ...,
        description="The properties to be used for embedding the content",
        default_factory=dict,
    )
