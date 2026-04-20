# from unittest.mock import patch, MagicMock

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
