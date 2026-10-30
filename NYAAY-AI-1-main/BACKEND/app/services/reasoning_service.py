from typing import Dict, Any, Optional
import uuid
import logging
from app.ai.orchestrator import rag_orchestrator
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

class ReasoningRequest(BaseModel):
    user_facts: str
    tenant_id: Optional[str] = "global"
    conversation_id: Optional[str] = None
    history: Optional[list] = []
    language: Optional[str] = "en"
    detected_lang: Optional[str] = "en"

from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.services.title_service import generate_conversation_title_async
import json

class ReasoningService:
    async def generate_analysis(self, request: ReasoningRequest, user_id: str, db: Session, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """
        Generates a structured legal reasoning analysis using the RAG orchestrator,
        saving the context in a persistent conversation.
        """
        from app.models.chat import Conversation, Message, FeatureType, MessageRole
        
        logger.info("Generating legal reasoning analysis")
        
        conversation = None
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            ).first()

            if conversation and conversation.feature_type != FeatureType.legal_reasoning:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Conversation does not belong to legal reasoning.")
            
        if not conversation:
            # Create a temporary title, can be updated asynchronously later
            title = "New Conversation"
            conversation = Conversation(
                user_id=user_id,
                title=title,
                feature_type=FeatureType.legal_reasoning
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            # Asynchronous title generation
            background_tasks.add_task(generate_conversation_title_async, conversation.id, request.user_facts)
            
        # Save User Message
        user_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.user,
            content=request.user_facts
        )
        db.add(user_msg)
        db.commit()

        # Translation IN
        detected_lang = request.detected_lang or "en"
        language = request.language or "en"
        
        query_for_rag = request.user_facts
        if detected_lang != "en":
            from app.core.translate import translate_in
            query_for_rag = await translate_in(query_for_rag, detected_lang)

        # Trigger the pipeline with REASONING task_type
        # Legal reasoning is limited to the public statutory corpus. Never
        # trust a client-provided tenant ID here: it could target another
        # user's uploaded-document namespace.
        filters = {"tenant_id": "global"}
        
        # Load real history from DB instead of request.history
        past_messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at.asc()).all()
        # the history parameter is expecting list of dicts. We skip the very last message which is the current one.
        formatted_history = [{"role": m.role.value, "content": m.content} for m in past_messages[:-1]]
        
        response = rag_orchestrator.trigger_pipeline(
            question=query_for_rag,
            filters=filters,
            history=formatted_history,
            task_type="REASONING",
            language=language
        )
        
        assistant_content = response.get("answer", "Failed to generate analysis.")
        
        # Translation OUT
        if language != "en":
            from app.core.translate import translate_out
            assistant_content, _ = await translate_out(assistant_content, language)
        
        assistant_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=assistant_content
        )
        db.add(assistant_msg)
        db.commit()
        
        # Format the response
        return {
            "conversation_id": conversation.id,
            "analysis_id": str(uuid.uuid4()),
            "content": assistant_content,
            "citations": response.get("citations", []),
            "created_at": datetime.utcnow().isoformat()
        }

reasoning_service = ReasoningService()
