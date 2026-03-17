# Standard Library Imports
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

# Third-Party Imports
from sqlalchemy import func
from sqlmodel import Column, DateTime, Field, SQLModel


class Conversation(SQLModel, table=True):
    """Database model for a conversation between a user and the AI."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    title: Optional[str] = None
    created_at: datetime = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()),
    )


class Message(SQLModel, table=True):
    """Database model for individual messages within a conversation."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id")
    user_message: str
    ai_response: str
    ai_model: str
    tokens_used: int
    latency_ms: float
    created_at: datetime = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )


class ChatRequest(SQLModel):
    """Schema for incoming chat requests."""

    conversation_id: Optional[UUID] = None
    user_id: UUID
    user_message: str
    title: Optional[str] = None  # Optional title for the conversation


class ChatResponse(SQLModel):
    """Schema for outgoing chat responses."""

    conversation_id: UUID
    title: Optional[str]
    ai_response: str
    ai_model: str
    tokens_used: int
    latency_ms: float
    created_at: datetime
    history: list[Message]
