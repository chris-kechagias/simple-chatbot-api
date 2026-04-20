from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.models import Conversation, Message

# ----------------------------------------------------
# 1. TEST -> READ ROUTES
# ----------------------------------------------------


def test_get_conversations_for_user_empty(client):
    """Returns empty list when user has no conversations"""
    user_id = uuid4()
    response = client.get(f"/chat/conversations/{user_id}")
    assert response.status_code == 200
    assert response.json() == []


def test_get_conversations_for_user(client, session):
    """Returns conversations for a given user"""
    # Create a conversation directly in the test DB
    user_id = uuid4()
    conv = Conversation(user_id=user_id, prompt_key="stoic", title="Test Chat")
    session.add(conv)
    session.commit()

    response = client.get(f"/chat/conversations/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Chat"


def test_get_conversations_invalid_user_id(client):
    """Returns 422 when user_id is not a valid UUID"""
    response = client.get("/chat/conversations/not-a-uuid")
    assert response.status_code == 422


def test_get_chat_history(client, session):
    """Returns message history for a given conversation ID"""
    # Create a conversation directly in the test DB
    conv = Conversation(user_id=uuid4(), prompt_key="stoic", title="Test Chat History")
    session.add(conv)
    session.commit()

    # Create a message history directly in the test DB
    msg = Message(
        conversation_id=conv.id,
        user_message="Hello chatbot",
        ai_response="Hi there",
        ai_model="gpt-5.4-mini",
        tokens_used=10,
        latency_ms=100.0,
    )
    session.add(msg)
    session.commit()

    response = client.get(f"/chat/{conv.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_message"] == "Hello chatbot"
    assert data[0]["ai_response"] == "Hi there"
    assert data[0]["ai_model"] == "gpt-5.4-mini"
    assert data[0]["tokens_used"] == 10
    assert data[0]["latency_ms"] == 100.0


def test_get_chat_history_not_found(client):
    """Returns 404 when conversation ID is not found"""
    response = client.get(f"/chat/{uuid4()}")
    assert response.status_code == 404


def test_get_chat_history_invalid_id(client):
    """Returns 422 when conversation_id is not a valid UUID"""
    response = client.get("/chat/not-a-uuid")
    assert response.status_code == 422


# ----------------------------------------------------
# 2. TEST -> WRITE ROUTES - (POST/PATCH/DELETE)
# ----------------------------------------------------


async def mock_streaming_response():
    """Mock streaming response generator for testing"""
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta.content = "Hello. This is a streamed response."
    chunk.usage = None
    yield chunk

    # Last chunk with usage info
    last = MagicMock()
    last.choices = [MagicMock()]
    last.choices[0].delta.content = None
    last.usage = MagicMock()
    last.model = "gpt-5.4-mini"
    yield last


@patch(
    "app.controllers.chat.get_chat_completion_stream",
    return_value=mock_streaming_response(),
)
def test_create_chat(mock_openai, client):
    """Tests the /chat POST endpoint with a mocked streaming response"""
    response = client.post(
        "/chat/",
        json={
            "user_id": str(uuid4()),
            "user_message": "Hello. This is a streamed response.",
        },
    )
    assert response.status_code == 200


@patch(
    "app.controllers.chat.get_chat_completion_stream",
    side_effect=Exception("OpenAI API error"),
)
def test_create_chat_internal_server_error(mock_openai, client):
    """Tests that the /chat POST endpoint returns a 500 status code when an exception occurs during streaming"""
    response = client.post(
        "/chat/",
        json={
            "user_id": str(uuid4()),
            "user_message": "This will trigger an internal server error.",
        },
    )
    assert response.status_code == 200
    assert "Stream interrupted" in response.text
