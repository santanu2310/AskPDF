from typing import List, Literal, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

config = ConfigDict(from_attributes=True)


class MessagePayload(BaseModel):
    temp_id: str
    conv_id: Optional[UUID]
    message: str
    file_id: UUID


class Citation(BaseModel):
    text: str
    source: str


class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]


class Message(BaseModel):
    id: UUID
    text: str
    citations: Optional[list[Citation]] = None
    conversation_id: UUID
    role: Literal["user", "assistant"]
    time_stamp: datetime


class MessageResponse(BaseModel):
    """
    Represents the complete response for a single turn in a conversation.
    """

    conversation_id: UUID = Field(
        description="The unique identifier for the entire conversation."
    )
    file_id: Optional[UUID] = Field(
        default=None,
        description="The identifier for the file or document context of the conversation.",
    )

    user_message: Message = Field(
        description="The user's message that initiated this turn."
    )
    assistant_message: Message = Field(
        description="The assistant's reply to the user's message."
    )

    created_at: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the conversation was first created. Only present on the first turn.",
    )


class DeleteConversation(BaseModel):
    id: UUID


class DocumentOut(BaseModel):
    id: UUID
    # Assuming your Document model has a 'file_name' or similar attribute
    file_name: str
    created_at: datetime

    model_config = config


# --- Schema for a single Message ---
# Defines the fields for each message within the conversation.
class MessageOut(BaseModel):
    id: UUID
    content: str
    role: str  # You could use Literal["user", "assistant"] for stricter validation
    created_at: datetime

    model_config = config


class Conversation(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    title: str
    updated_at: datetime

    # This allows the schema to be created from a database model
    model_config = config


class ConversationDetailOut(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    # The relationships are represented as lists of their respective schemas
    messages: List[MessageOut]
    documents: List[DocumentOut]

    model_config = config
