"""
Controller functions for chat-related operations,
including handling new and existing conversations,
retrieving conversation history and managing conversation metadata.
This module defines the core business logic for processing chat requests,
interacting with the database, and communicating with the OpenAI API.
It includes error handling to ensure robust operation and clear feedback to API clients.

"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from uuid import UUID

from fastapi.responses import StreamingResponse
from sqlmodel import select

from ..core import SessionDep, config, engine
from ..core.errors import ConversationNotFoundException
from ..models import (
    ChatRequest,
    ChatResponse,
    Conversation,
    ConversationSummary,
    Message,
)
from ..services import (
    get_chat_completion,
    get_chat_completion_stream,
    update_conversation_summary,
    update_conversation_title,
)
from ..utils import trim_messages_by_tokens

# Initialize logger for this module
logger = logging.getLogger(__name__)


async def chat_streaming_controller(request: ChatRequest, db: SessionDep):
    """
    Handles both new and existing conversations via streaming.

    Creates a new conversation if no conversation_id is provided, or retrieves
    the existing one. Builds the full message history, streams the OpenAI
    response, persists the result to the database upon completion, and
    triggers background utilities.

    Raises ConversationNotFoundException if the provided conversation_id does not exist.

    """
    # 1. Determine if this is a new conversation
    is_new_conversation = not request.conversation_id

    if is_new_conversation:
        conversation = Conversation(
            user_id=request.user_id, title=request.title or "New Chat..."
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        history = []
    else:
        conversation = db.get(Conversation, request.conversation_id)
        if not conversation:
            raise ConversationNotFoundException(request.conversation_id)

        # Get history (reversed to get chronological order)
        history_objs = db.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(config.context_window_size)
        ).all()
        history = list(reversed(history_objs))

    # 2. Build history for OpenAI
    messages = [{"role": "system", "content": config.openai_system_prompt}]
    for msg in history:
        messages.append({"role": "user", "content": msg.user_message})
        messages.append({"role": "assistant", "content": msg.ai_response})
    messages.append({"role": "user", "content": request.user_message})

    # Trim messages if they exceed the token limit, and update the conversation summary with evicted messages
    trimmed_messages = trim_messages_by_tokens(messages, config.openai_max_input_tokens)

    # Identify which messages were evicted (excluding the system prompt and the latest user message)
    evicted = [m for m in messages[1:-1] if m not in trimmed_messages]

    if evicted:
        # Update the conversation summary in the background with the evicted messages
        asyncio.create_task(
            update_conversation_summary(engine, conversation.id, evicted)
        )

    if conversation.summary:
        # If there is an existing summary, append it to the content of the oldest message in the trimmed context
        trimmed_messages[0]["content"] += (
            f"\n\nPAST CONTEXT SUMMARY: {conversation.summary}"
        )

    # 3. The Generator
    async def stream_generator():
        full_content = ""
        metadata = {}
        start_time = time.perf_counter()

        try:
            async for chunk in get_chat_completion_stream(trimmed_messages):
                # Handle content chunks
                if chunk.choices and chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    full_content += delta
                    yield f"data: {json.dumps({'content': delta})}\n\n"

                # Handle usage/metadata chunk (usually the last one)
                if chunk.usage:
                    metadata = {
                        "model": chunk.model,
                        "tokens": chunk.usage.total_tokens,
                    }

            # 4. STREAM SUCCESSFUL - PERSIST DATA
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Save the message record
            new_msg = Message(
                conversation_id=conversation.id,
                user_message=request.user_message,
                ai_response=full_content,
                ai_model=metadata.get("model", config.openai_model),
                tokens_used=metadata.get("tokens", 0),
                latency_ms=latency_ms,
            )
            conversation.updated_at = datetime.now(timezone.utc)
            db.add(new_msg)
            db.add(conversation)
            db.commit()

            # 5. POST-CHAT UTILITIES
            # Only generate title if it's the very first message of a new chat
            if is_new_conversation:
                asyncio.create_task(
                    update_conversation_title(
                        engine, conversation.id, request.user_message
                    )
                )

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Mid-stream failure: {e}")
            yield f"data: {json.dumps({'error': 'Stream interrupted'})}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


async def chat_controller(request: ChatRequest, db: SessionDep) -> ChatResponse:
    """
    Handles both new and existing conversations.

    Creates a new conversation if no conversation_id is provided, or retrieves
    the existing one. Builds the full message history, calls OpenAI, persists
    the result, and returns the response.

    Raises ConversationNotFoundException if the provided conversation_id does not exist.
    """
    if not request.conversation_id:
        # Create a new conversation if no conversation_id is provided
        conversation = Conversation(
            user_id=request.user_id, title=request.title or "New Chat..."
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        if not request.title:
            asyncio.create_task(
                update_conversation_title(engine, conversation.id, request.user_message)
            )

        history = []
    else:
        # Retrieve existing conversation
        conversation = db.get(Conversation, request.conversation_id)
        if not conversation:
            raise ConversationNotFoundException(request.conversation_id)
        history = db.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(config.context_window_size)
        ).all()

        history = list(reversed(history))

    # Build the message array for the OpenAI API, starting with a system prompt and the conversation history
    messages = [{"role": "system", "content": config.openai_system_prompt}]
    for msg in history:
        if not msg.ai_response:
            continue
        messages.append({"role": "user", "content": msg.user_message})
        messages.append({"role": "assistant", "content": msg.ai_response})
    messages.append({"role": "user", "content": request.user_message})

    # Trim messages if they exceed the token limit, and update the conversation summary with evicted messages
    trimmed_messages = trim_messages_by_tokens(messages, config.openai_max_input_tokens)

    # Identify which messages were evicted (excluding the system prompt and the latest user message)
    evicted = [m for m in messages[1:-1] if m not in trimmed_messages]

    if evicted:
        # Update the conversation summary in the background with the evicted messages
        asyncio.create_task(
            update_conversation_summary(engine, conversation.id, evicted)
        )

    if conversation.summary:
        # If there is an existing summary, append it to the content of the oldest message in the trimmed context
        trimmed_messages[0]["content"] += (
            f"\n\nPAST CONTEXT SUMMARY: {conversation.summary}"
        )

    # Measure latency for the OpenAI API call
    start = time.perf_counter()
    ai_response = await get_chat_completion(trimmed_messages)
    latency_ms = (time.perf_counter() - start) * 1000

    # Create a new Message record with the user's message, AI response, and metadata
    message_record = Message(
        conversation_id=conversation.id,
        user_message=request.user_message,
        ai_response=ai_response["content"],
        ai_model=ai_response["model"],
        tokens_used=ai_response["tokens"],
        latency_ms=latency_ms,
    )

    conversation.updated_at = datetime.now(timezone.utc)
    db.add_all([message_record, conversation])
    db.commit()
    db.refresh(message_record)

    # Return the response with the updated conversation and message details
    return ChatResponse(
        conversation_id=conversation.id,
        title=conversation.title,
        history=[Message.model_validate(msg) for msg in history] + [message_record],
        **message_record.model_dump(exclude={"id", "conversation_id", "user_message"}),
    )


async def get_chat_by_id_controller(
    conversation_id: UUID, db: SessionDep
) -> list[Message]:
    """
    Retrieves a conversation and its message history by conversation ID.

    Raises ConversationNotFoundException if the conversation does not exist.
    """
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise ConversationNotFoundException(conversation_id)

    return db.exec(
        select(Message).where(Message.conversation_id == conversation.id)
    ).all()


async def get_all_conversations_for_user_controller(
    user_id: UUID, db: SessionDep
) -> list[ConversationSummary]:
    """
    Retrieves all conversations for a given user.

    Returns a list of ConversationSummary objects, which include conversation ID, title, and timestamps.
    """
    conversations = db.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    return [
        ConversationSummary(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )
        for conv in conversations
    ]


async def patch_conversation_controller(
    conversation_id: UUID, title: str, db: SessionDep
) -> ConversationSummary:
    """
    Updates the title of an existing conversation.

    Raises ConversationNotFoundException if the conversation does not exist.
    """
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise ConversationNotFoundException(conversation_id)

    conversation.title = title
    conversation.updated_at = datetime.now(timezone.utc)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return ConversationSummary(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


async def delete_conversation_controller(conversation_id: UUID, db: SessionDep) -> None:
    """
    Deletes a conversation and all its associated messages.

    Raises ConversationNotFoundException if the conversation does not exist.
    """
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise ConversationNotFoundException(conversation_id)

    # Delete all messages associated with the conversation
    messages = db.exec(
        select(Message).where(Message.conversation_id == conversation.id)
    ).all()
    for message in messages:
        db.delete(message)
    db.flush()
    # Delete the conversation itself
    db.delete(conversation)
    db.commit()
