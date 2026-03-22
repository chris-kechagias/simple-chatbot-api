# Standard Library Imports
import time
from datetime import datetime, timezone
from uuid import UUID

# Third-Party Imports
from sqlmodel import select

# Local/First-Party Imports
from ..core import SessionDep, config
from ..core.errors import ConversationNotFoundException
from ..models import (
    ChatRequest,
    ChatResponse,
    Conversation,
    ConversationSummary,
    Message,
)
from ..services import get_chat_completion


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
            user_id=request.user_id, title=request.title or request.user_message[:50]
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        history = []
    else:
        # Retrieve existing conversation
        conversation = db.get(Conversation, request.conversation_id)
        if not conversation:
            raise ConversationNotFoundException(request.conversation_id)
        history = db.exec(
            select(Message).where(Message.conversation_id == conversation.id)
        ).all()

    # Build the message array for the OpenAI API, starting with a system prompt and the conversation history
    messages = [{"role": "system", "content": config.openai_system_prompt}]
    for msg in history:
        messages.append({"role": "user", "content": msg.user_message})
        messages.append({"role": "assistant", "content": msg.ai_response})
    messages.append({"role": "user", "content": request.user_message})

    # Measure latency for the OpenAI API call
    start = time.time()
    ai_response = await get_chat_completion(messages)
    latency_ms = (time.time() - start) * 1000

    # Create a new Message record with the user's message, AI response, and metadata
    message_record = Message(
        conversation_id=conversation.id,
        user_message=request.user_message,
        ai_response=ai_response.choices[0].message.content,
        ai_model=ai_response.model,
        tokens_used=ai_response.usage.total_tokens,
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
        history=history + [message_record],
        **message_record.model_dump(exclude={"id", "conversation_id", "user_message"}),
    )


async def get_chat_by_id(conversation_id: UUID, db: SessionDep) -> list[Message]:
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


async def get_all_conversations_for_user(
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
