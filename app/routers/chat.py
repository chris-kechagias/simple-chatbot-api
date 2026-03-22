# Standard Library Imports
from uuid import UUID

# Third-Party Imports
from fastapi import APIRouter, status

# Local/First-Party Imports
from ..controllers import (
    chat_controller,
    get_all_conversations_for_user,
    get_chat_by_id,
)
from ..core import SessionDep
from ..models import ChatRequest, ChatResponse, ConversationSummary, Message

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
    return await get_all_conversations_for_user(user_id, db)


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
    return await get_chat_by_id(conversation_id, db)


# ----------------------------------------------------
# 2. WRITE ROUTES - Create and Continue Conversations
# ----------------------------------------------------


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Conversation not found"},
        500: {"description": "Internal server error"},
    },
    summary="Send a chat message",
    description="Endpoint to send a chat message to the AI. "
    "If no conversation ID is provided, a new conversation will be created. "
    "The response includes the AI's reply and conversation history.",
)
async def create_chat_router(request: ChatRequest, db: SessionDep) -> ChatResponse:
    """
    Start a new conversation and get the first AI response.

    Creates a fresh conversation record, sends the user's message to OpenAI,
    and returns the AI reply along with the conversation ID. Use the returned
    conversation_id in subsequent requests to POST /chat/{conversation_id}
    to continue the conversation.
    """
    request.conversation_id = None
    return await chat_controller(request, db)


@router.post(
    "/{conversation_id}",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Conversation not found"},
        500: {"description": "Internal server error"},
    },
    summary="Send a chat message to an existing conversation",
    description="Endpoint to send a chat message to an existing conversation. "
    "The conversation ID must be provided in the URL path. "
    "The response includes the AI's reply and updated conversation history.",
)
async def continue_chat_router(
    conversation_id: UUID, request: ChatRequest, db: SessionDep
) -> ChatResponse:
    """
    Endpoint to continue an existing conversation by sending a new chat message.
    The conversation ID is provided in the URL path, and the user's message is included in the request body.
    The controller function will handle retrieving the conversation, interacting with the OpenAI service,
    and updating the conversation state in the database. If the conversation ID does not exist, a 404 error will be returned.
    """
    request.conversation_id = conversation_id
    return await chat_controller(request, db)
