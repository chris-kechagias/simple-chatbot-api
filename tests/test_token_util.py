from app.utils import trim_messages_by_tokens


def test_trim_messages_by_tokens_no_trimming_enabled():
    """Verify that messages are not trimmed when the total token count is within the limit."""
    # Create a list of messages that exceeds the token limit
    messages = [
        {"role": "system", "content": "System prompt."},
        {"role": "user", "content": "Hello."},
    ]
    result = trim_messages_by_tokens(messages, max_input_tokens=4000)
    assert result == messages


def test_trim_messages_by_tokens():
    """Verify that messages are trimmed correctly when the total token count exceeds the limit."""
    # Create a list of messages that exceeds the token limit
    messages = [
        {"role": "system", "content": "System prompt."},
        {"role": "user", "content": "User message 1."},
        {"role": "assistant", "content": "Assistant response 1."},
        {"role": "user", "content": "User message 2."},
        {"role": "assistant", "content": "Assistant response 2."},
        {"role": "user", "content": "User message 3."},
        {"role": "assistant", "content": "Assistant response 3."},
        {"role": "user", "content": "User message 4."},
    ]

    # Set a low token limit to force trimming
    max_input_tokens = 50

    trimmed_messages = trim_messages_by_tokens(messages, max_input_tokens)

    # The trimmed messages should include the system prompt and the latest user message
    assert trimmed_messages[0]["content"] == "System prompt."
    assert trimmed_messages[-1]["content"] == "User message 4."
    assert len(trimmed_messages) < len(messages)


def test_trim_messages_by_tokens_to_minimum():
    """Verify that messages are trimmed down to the minimum (system prompt + latest user message) when the token limit is very low."""
    # Create a list of messages that exceeds the token limit
    messages = [
        {"role": "system", "content": "System prompt."},
        {"role": "user", "content": "Old message."},
        {"role": "assistant", "content": "Old response."},
        {"role": "user", "content": "Latest message."},
    ]

    # Set a very low token limit to force trimming to minimum
    max_input_tokens = 20

    trimmed_messages = trim_messages_by_tokens(messages, max_input_tokens)

    # The trimmed messages should include only the system prompt and the latest user message
    assert len(trimmed_messages) == 2
    assert trimmed_messages[0]["content"] == "System prompt."
    assert trimmed_messages[1]["content"] == "Latest message."
