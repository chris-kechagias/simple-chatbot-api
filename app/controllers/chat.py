# Standard Library Imports
import time
from datetime import datetime, timezone

# Third-Party Imports
from sqlmodel import select

# Local/First-Party Imports
from ..config import config
from ..database import SessionDep
from ..models import ChatRequest, ChatResponse, Conversation, Message
from ..services.openai_service import get_chat_completion
from ..utils.errors import ConversationNotFoundException


async def chat_controller(request: ChatRequest, db: SessionDep) -> ChatResponse:
    """
    Controller function to handle chat requests.
    This function manages both new conversations and existing conversations
    based on the presence of a conversation ID in the request.
    It interacts with the OpenAI service to get AI responses and manages conversation state in the database.
    If a conversation ID is provided but not found in the database, it raises a ConversationNotFoundException,
    which is handled by the global error handler to return an appropriate error response to the client.
    """
    if not request.conversation_id:
        # Create a new conversation if no conversation_id is provided
        conversation = Conversation(
            user_id=request.user_id, title=request.title or request.user_message[:50]
        )
        # Save the new conversation to the database
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Build the message array for the OpenAI API, starting with a system prompt and the user's message
        messages = [
            {"role": "system", "content": config.openai_system_prompt},
            {"role": "user", "content": request.user_message},
        ]

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
        # Save the new message to the database
        db.add(message_record)
        db.commit()
        db.refresh(message_record)

        # Return the response with the new conversation and message details
        return ChatResponse(
            conversation_id=conversation.id,
            title=conversation.title,
            ai_response=message_record.ai_response,
            ai_model=message_record.ai_model,
            tokens_used=message_record.tokens_used,
            latency_ms=message_record.latency_ms,
            created_at=message_record.created_at,
            history=[message_record],
        )
    else:
        # Retrieve existing conversation
        conversation = db.get(Conversation, request.conversation_id)
        if not conversation:
            # Conversation not found, raise an exception to be handled by the global error handler
            raise ConversationNotFoundException(request.conversation_id)

        # Retrieve conversation history to provide context for the AI response
        history = db.exec(
            select(Message).where(Message.conversation_id == conversation.id)
        ).all()

        # Build the message history for the OpenAI API
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
        # Save the new message to the database
        db.add(message_record)
        db.commit()
        db.refresh(message_record)

        # Update conversation's updated_at timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        db.add(conversation)
        db.commit()

        # Return the response with the updated conversation and message details
        return ChatResponse(
            conversation_id=conversation.id,
            title=conversation.title,
            ai_response=message_record.ai_response,
            ai_model=message_record.ai_model,
            tokens_used=message_record.tokens_used,
            latency_ms=message_record.latency_ms,
            created_at=message_record.created_at,
            history=history + [message_record],
        )
