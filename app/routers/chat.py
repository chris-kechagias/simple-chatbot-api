# Standard Library Imports
from uuid import UUID

# Third-Party Imports
from fastapi import APIRouter, status

# Local/First-Party Imports
from ..controllers import chat_controller
from ..database import SessionDep
from ..models import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


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
