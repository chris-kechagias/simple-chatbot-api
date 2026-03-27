import logging

from sqlmodel import Session

from ..core import config
from ..models.chat import Conversation
from .openai_service import get_chat_completion

logger = logging.getLogger(__name__)


async def update_conversation_summary(
    engine, conversation_id: str, evicted_messages: list[dict]
):
    """
    Background task to update the conversation summary with messages
    that were trimmed from the active context.
    """
    try:
        with Session(engine) as session:
            conv = session.get(Conversation, conversation_id)
            if not conv:
                return

            # Format the messages for the LLM
            new_content = "\n".join(
                [f"{m['role']}: {m['content']}" for m in evicted_messages]
            )

            prompt = f"""
            Update the existing summary with the new conversation details provided.
            Keep it concise (max 200 words). Focus on key facts and user preferences.
            
            EXISTING SUMMARY: {conv.summary or "None"}
            NEW DETAILS: {new_content}
            
            NEW SUMMARY:
            """

            # Use a cheaper model or standard gpt-5-mini
            response = await get_chat_completion(
                model=config.openai_utility_model,
                messages=[{"role": "user", "content": prompt}],
            )
            new_summary = response.get("content")

            if new_summary:
                conv.summary = new_summary
                session.add(conv)
                session.commit()
                logger.info(f"Summary updated for conversation {conversation_id}")

    except Exception as e:
        logger.error(f"Failed to update summary: {e}")
