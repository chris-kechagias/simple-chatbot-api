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


