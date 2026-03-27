import logging

import tiktoken

logger = logging.getLogger(__name__)


def trim_messages_by_tokens(
    messages: list[dict], max_input_tokens: int = 4000
) -> list[dict]:
    """
    Trims the conversation history to fit within the token limit for the OpenAI API.

    This function calculates the total tokens used by the messages and removes the oldest messages
    until the total tokens are within the allowed limit.
    """
    try:
        # GPT-5 and o1 models use the o200k_base tokenizer
        encoding = tiktoken.get_encoding("o200k_base")
    except Exception:
        # Fallback to 4o encoding which is also o200k_base compatible
        encoding = tiktoken.encoding_for_model("gpt-4o")

    def count_tokens(msgs):
        # Base overhead: ~3 tokens per message + 3 tokens for the response header
        return sum(len(encoding.encode(m["content"])) + 3 for m in msgs) + 3

    current_total = count_tokens(messages)

    if current_total <= max_input_tokens:
        return messages

    logger.warning(
        "Input context too large. Trimming history.",
        extra={"current_tokens": current_total, "limit": max_input_tokens},
    )

    system_prompt = messages[0]
    latest_user_msg = messages[-1]
    history = messages[1:-1]

    # Remove oldest history (User/AI pairs) until it is under the input limit
    while (
        count_tokens([system_prompt] + history + [latest_user_msg]) > max_input_tokens
        and history
    ):
        # Remove both user and assistant messages
        history.pop(0)
        history.pop(0)

    return [system_prompt] + history + [latest_user_msg]
