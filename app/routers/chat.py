"""
This module defines the API routes for chat-related operations, including creating new conversations,
continuing existing conversations, retrieving conversation history, updating conversation titles,
and deleting conversations. Each route is designed to handle specific HTTP methods and endpoints,
and interacts with the corresponding controller functions to perform the necessary business logic.

"""

from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from ..controllers import (
    chat_streaming_controller,
    delete_conversation_controller,
    get_all_conversations_for_user_controller,
    get_chat_by_id_controller,
    patch_conversation_controller,
)
from ..core import SessionDep
from ..models import (
    ChatRequest,
    ConversationSummary,
    Message,
    UpdateTitleRequest,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

# ----------------------------------------------------
# 1. READ ROUTES
# ----------------------------------------------------


@router.get(
    "/conversations/{user_id}",
    response_model=list[ConversationSummary],
    status_code=status.HTTP_200_OK,
    summary="Get all conversations for a user",
    description="Retrieve a list of all conversations for a given user ID. "
    "Returns a summary of each conversation, including the conversation ID, title, and timestamps.",
)
async def get_conversations_for_user_router(
    user_id: UUID, db: SessionDep
) -> list[ConversationSummary]:
    return await get_all_conversations_for_user_controller(user_id, db)


@router.get(
    "/{conversation_id}",
    response_model=list[Message],
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Conversation not found"}},
    summary="Get conversation history",
    description="Retrieve the full message history for a given conversation ID. "
    "Returns a list of messages in the order they were sent, including both user messages and AI responses.",
)
async def get_chat_history_router(
    conversation_id: UUID, db: SessionDep
) -> list[Message]:
    return await get_chat_by_id_controller(conversation_id, db)


# ----------------------------------------------------
# 2. WRITE ROUTES - (POST/PATCH/DELETE)
# ----------------------------------------------------


@router.post(
    "/",
    response_class=StreamingResponse,  # Tell FastAPI to expect a stream
    status_code=status.HTTP_200_OK,
    responses={
        500: {"description": "Internal server error"},
    },
    summary="Send a chat message",
    description="Endpoint to send a chat message and stream the response.",
)
async def create_chat_router(request: ChatRequest, db: SessionDep):
    # This now uses the streaming controller
    request.conversation_id = None
    return await chat_streaming_controller(request, db)


@router.post(
    "/{conversation_id}",
    response_class=StreamingResponse,  # Use StreamingResponse here too
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Conversation not found"},
        500: {"description": "Internal server error"},
    },
    summary="Send a chat message to an existing conversation",
)
async def continue_chat_router(
    conversation_id: UUID, request: ChatRequest, db: SessionDep
):
    # This now uses the streaming controller
    request.conversation_id = conversation_id
    return await chat_streaming_controller(request, db)


@router.patch(
    "/{conversation_id}/title",
    response_model=ConversationSummary,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Conversation not found"}},
    summary="Update conversation title",
    description="Endpoint to update the title of an existing conversation. "
    "The conversation ID is provided in the URL path, and the new title is included in the request body. "
    "Returns the updated conversation summary.",
)
async def update_conversation_title_router(
    conversation_id: UUID, request: UpdateTitleRequest, db: SessionDep
) -> ConversationSummary:
    return await patch_conversation_controller(conversation_id, request.title, db)


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Conversation not found"}},
    summary="Delete a conversation",
    description="Endpoint to delete an existing conversation and all its associated messages. "
    "The conversation ID is provided in the URL path. "
    "Returns a 204 No Content status on successful deletion.",
)
async def delete_conversation_router(conversation_id: UUID, db: SessionDep) -> None:
    return await delete_conversation_controller(conversation_id, db)
