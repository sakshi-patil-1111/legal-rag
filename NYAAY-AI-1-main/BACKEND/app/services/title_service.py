from app.models.chat import Conversation
from app.database.database import SessionLocal
import logging
import re

logger = logging.getLogger(__name__)

def generate_deterministic_title(prompt: str) -> str:
    """
    Deterministic local title generator.
    0 LLM calls, <1ms processing, 5-8 words max.
    Extracts directly from the user's original wording.
    """
    prompt = prompt.strip()
    if not prompt:
        return "New Conversation"
        
    # Split by whitespace (automatically handles excessive spaces)
    words = prompt.split()
    if not words:
        return "New Conversation"
        
    # Take the first ~7-8 words
    title_words = words[:8]
    title = " ".join(title_words)
    
    # Remove trailing punctuation from the cut string
    title = title.rstrip(".,;:!?")
    
    return title

def generate_conversation_title_async(conversation_id: str, prompt: str):
    """
    Background task to generate a title deterministically and save it to the DB.
    """
    try:
        new_title = generate_deterministic_title(prompt)
        
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.title = new_title
                db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to generate title asynchronously: {e}")
