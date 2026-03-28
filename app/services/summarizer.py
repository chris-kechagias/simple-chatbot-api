"""
This module defines the Summarizer service,
which is responsible for updating the conversation summary
with messages that have been evicted from the active context.

"""

import logging

from sqlmodel import Session

from ..core import config
from ..models.chat import Conversation
from .openai_service import generate_conversation_title, get_chat_completion

logger = logging.getLogger(__name__)


async def update_conversation_summary(
    engine, conversation_id: str, evicted_messages: list[dict]
):
    """
    Background task to update the conversation summary with messages
    that were trimmed from the active context.
    """
    # Don't start the LLM process if the evicted content is too small to matter
    if len(evicted_messages) < 2 and len(evicted_messages[0].get("content", "")) < 20:
        logger.debug(
            f"Skipping summary update for {conversation_id}: content too short."
        )
        return

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
            You are a specialized memory-compression module. 
            Your task is to merge NEW DETAILS into an EXISTING SUMMARY.
            
            STRICT RULES:
            1. Preserve all specific facts (names, technologies, specific numbers).
            2. Preserve user preferences (e.g., "User prefers Python", "User wants concise answers").
            3. Delete redundant greetings or filler.
            4. Keep the output under 200 words.
            5. Output ONLY the new summary text.

            EXISTING SUMMARY:
            {conv.summary or "No previous summary."}

            NEW DETAILS TO ADD:
            {new_content}

            UPDATED COMPREHENSIVE SUMMARY:
            """

            # Primary attempt with Nano utility model for efficiency
            response = await get_chat_completion(
                model=config.openai_utility_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise data extraction assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            new_summary = response.get("content")

            # --- FALLBACK LOGIC START ---
            # Fallback to Mini if Nano fails quality/presence check
            if not new_summary or len(new_summary.strip()) < 10:
                logger.warning(
                    f"Nano model ({config.openai_utility_model}) failed to provide a valid summary. Falling back to Mini."
                )
                response = await get_chat_completion(
                    model=config.openai_model,  # Use the primary gpt-5-mini
                    messages=[{"role": "user", "content": prompt}],
                )
                new_summary = response.get("content")
            # --- FALLBACK LOGIC END ---

            if new_summary:
                conv.summary = new_summary
                session.add(conv)
                session.commit()
                logger.info(f"Summary updated for conversation {conversation_id}")

    except Exception as e:
        logger.error(f"Failed to update summary: {e}")


async def update_conversation_title(engine, conversation_id, user_message: str):
    """"""
    try:
        with Session(engine) as session:
            conv = session.get(Conversation, conversation_id)
            if not conv:
                return
            title = await generate_conversation_title(user_message)
            if title:
                conv.title = title
                session.add(conv)
                session.commit()
                logger.info(f"Title updated for {conversation_id}: {title}")
    except Exception as e:
        logger.error(f"Title generation failed: {e}")
