# Standard Library Imports
import functools
from typing import Any, Callable

# Third-Party Imports
import openai

# Local/First-Party Imports
from ..config import config
from ..utils.errors import OpenAIServiceException


def handle_openai_errors(func: Callable) -> Callable:
    """Decorator to handle OpenAI API errors gracefully."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
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


@handle_openai_errors
async def get_chat_completion(messages: list[dict]) -> Any:
    """Sends a chat completion request to the OpenAI API."""
    response = await openai.chat.completions.create(
        model=config.openai_model,
        messages=messages,
        max_tokens=config.openai_max_tokens,
        temperature=config.openai_temperature,
    )
    return response
