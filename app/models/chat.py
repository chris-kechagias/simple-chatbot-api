"""
This module defines the database models and Pydantic schemas for the chat application.
It includes SQLModel classes for Conversations and Messages,
which represent the structure of the database tables,
as well as Pydantic models for request and response validation in the API endpoints.

"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Text, func
from sqlmodel import Column, DateTime, Field, SQLModel


class Conversation(SQLModel, table=True):
    """Database model for a conversation between a user and the AI."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    prompt_key: Optional[str] = Field(default="stoic")
    title: Optional[str] = None
    summary: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()),
    )


class ConversationSummary(SQLModel):
    """Response schema for conversation list items. Excludes user_id."""

    id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


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


class UpdateTitleRequest(BaseModel):
    title: str


class ChatRequest(SQLModel):
    """Schema for incoming chat requests."""

    conversation_id: Optional[UUID] = None
    user_id: UUID
    prompt_key: str | None = None
    user_message: str
    title: Optional[str] = None  # Optional title for the conversation


class ChatResponse(SQLModel):
    """Schema for outgoing chat responses."""

    conversation_id: UUID
    title: Optional[str]
    prompt_key: str
    ai_response: str
    ai_model: str
    tokens_used: int
    latency_ms: float
    created_at: datetime
    history: list[Message]
