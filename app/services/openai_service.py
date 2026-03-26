# Standard Library Imports
import asyncio
import functools
import logging
from typing import Awaitable, Callable, TypeVar

# Third-Party Imports
import openai
from openai import AsyncOpenAI

# Local/First-Party Imports
from ..core import config
from ..core.errors import OpenAIServiceException

# Initialize logger for this module
logger = logging.getLogger(__name__)

T = TypeVar("T")


def handle_openai_errors(
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """Decorator to handle OpenAI API errors gracefully."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except OpenAIServiceException:
            raise
        except openai.APITimeoutError:
            raise OpenAIServiceException(
                message="OpenAI API request timed out. Please try again later.",
                status_code=504,
                error_code="OPENAI_TIMEOUT",
            )
        except openai.APIError as e:
            status = getattr(e, "status_code", 502)
            raise OpenAIServiceException(
                message=f"OpenAI API error: {str(e)}",
                status_code=status,
                error_code="OPENAI_SERVICE_ERROR",
                details={"original_error": e.__class__.__name__},
            )
        except Exception as e:
            raise OpenAIServiceException(
                message=f"Internal system error processing AI request: {str(e)}",
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR",
            )

    return wrapper


client = AsyncOpenAI(api_key=config.openai_api_key)


@handle_openai_errors
async def get_chat_completion(messages: list[dict], max_retries: int = 2) -> dict:
    """Sends a chat completion request to the OpenAI API."""
    for attempt in range(max_retries + 1):
        response = await client.chat.completions.create(
            model=config.openai_model,
            messages=messages,
            max_completion_tokens=config.openai_max_completion_tokens,
        )
        choice = response.choices[0] if response.choices else None
        content = choice.message.content if choice and choice.message else ""

        if content:
            return {
                "content": content,
                "model": response.model,
                "tokens": response.usage.total_tokens if response.usage else 0,
            }

        # Handle empty response with exponential backoff
        if attempt < max_retries:
            wait_time = (attempt + 1) * 2
            logger.warning(
                f"Received empty response from OpenAI API. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})",
                extra={
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "next_retry_delay": wait_time,
                    "model": config.openai_model,
                },
            )
            await asyncio.sleep(wait_time)
            continue

    # All retries exhausted
    raise OpenAIServiceException(
        message="OpenAI consistently returned an empty response.",
        status_code=502,
        error_code="EMPTY_RESPONSE",
    )
