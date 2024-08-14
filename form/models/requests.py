from pydantic import BaseModel, Field


class ChatInput(BaseModel):
    message: str = Field(..., min_length=1, description="The user's input message")


class Document(BaseModel):
    content: str = Field(..., min_length=1, description="The content to be embedded")
    properties: dict = Field(
        ...,
        description="The properties to be used for embedding the content",
        default_factory=dict,
    )
