from unittest.mock import MagicMock, patch

import pytest

from app.services import update_conversation_summary


@pytest.mark.asyncio
@patch("app.services.summarizer.get_chat_completion")
@patch("app.services.summarizer.loader.build")
@patch("app.services.summarizer.Session")
async def test_update_conversation_summary_nano_success(
    mock_session, mock_loader_build, mock_get_chat_completion
):
    """Tests that the summarizer successfully updates the conversation summary
    using the Nano utility model when it provides a valid summary.
    """
    # configure the mock to return a conversation with no summary
    mock_conv = MagicMock()
    mock_conv.summary = None
    mock_session.return_value.__enter__.return_value.get.return_value = mock_conv

    # configure the loader to return a formatted prompt
    mock_loader_build.return_value = "Formated prompt"

    # configure the chat completion to return a valid summary
    mock_get_chat_completion.return_value = {
        "content": "New summarized content by Nano"
    }

    # call the function under test
    await update_conversation_summary(
        MagicMock(),
        "some-id",
        [
            {
                "role": "user",
                "content": "This is a long enough message to pass the skip check.",
            },
            {
                "role": "assistant",
                "content": "This is a long enough message to pass the skip check.",
            },
        ],
    )

    # assert that the conversation summary was updated and saved
    assert mock_conv.summary == "New summarized content by Nano"
    mock_loader_build.assert_called_once()
    mock_get_chat_completion.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.summarizer.get_chat_completion")
@patch("app.services.summarizer.loader.build")
@patch("app.services.summarizer.Session")
async def test_update_conversation_summary_mini_fallback(
    mock_session, mock_loader_build, mock_get_chat_completion
):
    """Tests that the summarizer successfully updates the conversation summary
    using the Fallback Mini utility model when it provides a valid summary.
    """
    # configure the mock to return a conversation with no summary
    mock_conv = MagicMock()
    mock_conv.summary = None
    mock_session.return_value.__enter__.return_value.get.return_value = mock_conv

    # configure the loader to return a formatted prompt
    mock_loader_build.return_value = "Formated prompt"

    # configure the chat completion to return a valid summary
    mock_get_chat_completion.side_effect = [
        {"content": ""},  # Nano fails to provide a valid summary (empty response)
        {
            "content": "New summarized content by Mini"
        },  # Mini successfully provides a valid summary
    ]

    # call the function under test
    await update_conversation_summary(
        MagicMock(),
        "some-id",
        [
            {
                "role": "user",
                "content": "This is a long enough message to pass the skip check.",
            },
            {
                "role": "assistant",
                "content": "This is a long enough message to pass the skip check.",
            },
        ],
    )

    # assert that the conversation summary was updated and saved
    assert mock_conv.summary == "New summarized content by Mini"
    mock_loader_build.assert_called_once()
    assert mock_get_chat_completion.call_count == 2


@pytest.mark.asyncio
async def test_update_conversation_summary_skips_short_content():
    """Tests that the summarizer skips updating the summary when the evicted content is too short to matter."""
    # call the function under test with short content
    evicted = [{"role": "user", "content": "Short msg"}]
    await update_conversation_summary(None, "some-id", evicted)


@pytest.mark.asyncio
@patch("app.services.summarizer.get_chat_completion")
@patch("app.services.summarizer.Session")
async def test_update_conversation_summary_conv_not_found(
    mock_session, mock_completion
):
    """Tests that the summarizer returns early without trying to generate a summary when the conversation is not found in the database."""
    # configure the mock to not return any conversation
    mock_session.return_value.__enter__.return_value.get.return_value = None

    # call the function under test
    await update_conversation_summary(
        MagicMock(),
        "some-id",
        [
            {
                "role": "user",
                "content": "This is a long enough message to pass the skip check.",
            },
            {
                "role": "assistant",
                "content": "This is a long enough message to pass the skip check.",
            },
        ],
    )

    # assert that the function returns early without trying to generate a summary
    mock_completion.assert_not_called()
