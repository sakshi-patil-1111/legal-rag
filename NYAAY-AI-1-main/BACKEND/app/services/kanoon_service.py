import json
from google import genai
from google.genai import types
from app.core.config import settings
from app.schemas.kanoon import KanoonQueryRequest, KanoonQueryResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException
import asyncio
import concurrent.futures
import re

# ─── Shared thread-pool for blocking Groq calls ──────────────────────────────
_translator_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="translator")


def _detect_script_lang(text: str) -> str:
    """Fast regex-based language detection from query script. Returns BCP-47 code."""
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"
    if re.search(r'[\u0980-\u09FF]', text):
        return "bn"
    if re.search(r'[\u0B80-\u0BFF]', text):
        return "ta"
    return "en"


class KanoonService:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY or "DUMMY_KEY_FOR_TESTING"
        self.client = genai.Client(api_key=api_key)

    # ─────────────────────────────────────────────────────────────────────────
    # SYNCHRONOUS /query endpoint (used by KnowYourKanoon.jsx)
    # ─────────────────────────────────────────────────────────────────────────
    async def query(self, request: KanoonQueryRequest, user_id: str, db: Session, background_tasks) -> KanoonQueryResponse:
        detected_lang = request.detected_lang or "en"
        language = request.language or "en"

        # Always auto-detect from script — overrides any stale frontend value
        auto_lang = _detect_script_lang(request.question)
        if auto_lang != "en":
            detected_lang = auto_lang
            if language == "en":
                language = auto_lang

        from app.models.chat import Conversation, Message, FeatureType, MessageRole
        from app.ai.orchestrator import rag_orchestrator
        from app.services.title_service import generate_conversation_title_async

        conversation = None

        if request.conversation_id:
            from app.models.user import User
            db_user = db.query(User).filter(User.firebase_uid == user_id).first()
            target_uids = [user_id]
            if db_user:
                old_users = db.query(User).filter(User.email == db_user.email).all()
                for u in old_users:
                    target_uids.append(u.firebase_uid)

            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id.in_(target_uids)
            ).first()

            if conversation and conversation.feature_type != FeatureType.know_kanoon:
                raise HTTPException(status_code=400, detail="Conversation does not belong to Know Your Kanoon.")

        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                title="New Conversation",
                feature_type=FeatureType.know_kanoon
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            background_tasks.add_task(generate_conversation_title_async, conversation.id, request.question)

        user_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.user,
            content=request.question
        )
        db.add(user_msg)
        db.commit()

        past_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.asc()).all()
        formatted_history = [{"role": m.role.value, "content": m.content} for m in past_messages[:-1]]

        filters = {"tenant_id": "global"}

        # ── PERF: kick off translate_in CONCURRENTLY with RAG ─────────────────
        # translate_in is a Groq HTTP call (~3-5s). We run it in a thread so it
        # overlaps with the RAG pipeline's embedding + retrieval + generation.
        translate_future = None
        if detected_lang != "en":
            from app.core.translate import translate_in as _translate_in_fn
            loop = asyncio.get_event_loop()
            # Run the async coroutine in the background — we await it right before
            # passing search_query to the orchestrator.
            translate_task = asyncio.create_task(
                _translate_in_fn(request.question, detected_lang)
            )
        else:
            translate_task = None

        # ── If we need a translated query, await it now (should be fast since
        #    we fired it immediately above; RAG hasn't started yet in this path
        #    but Groq latency is already in flight).
        if translate_task is not None:
            search_query = await translate_task
        else:
            search_query = request.question

        # Acronym expansion
        expansions = {
            "RTI": "RTI Right to Information",
            "FIR": "FIR First Information Report Police",
            "consumer forum": "consumer dispute redressal",
            "rera": "Real Estate Regulatory Authority",
        }
        for acr, exp in expansions.items():
            search_query = re.sub(rf'\b{acr}\b', exp, search_query, flags=re.IGNORECASE)

        # ── RAG ───────────────────────────────────────────────────────────────
        response_data = await asyncio.to_thread(
            rag_orchestrator.trigger_pipeline,
            search_query,
            filters,
            formatted_history,
            "QA",
            language,
        )

        citations = response_data.get("citations", [])
        raw_answer = response_data.get("answer", "No answer generated.")

        # Extract executive summary
        dynamic_summary = "Response generated based on retrieved legal knowledge."
        try:
            parsed_ans = json.loads(re.sub(r'^```(?:json)?\s*|\s*```$', '', raw_answer.strip()))
            if "problemAndRights" in parsed_ans and "summary" in parsed_ans["problemAndRights"]:
                dynamic_summary = parsed_ans["problemAndRights"]["summary"]
        except Exception:
            exec_summary_match = re.search(r'(?i)##\s*Executive Summary\s*\n(.*?)(?=\n##|\Z)', raw_answer, re.DOTALL)
            if exec_summary_match:
                dynamic_summary = exec_summary_match.group(1).strip()
                new_raw = raw_answer[:exec_summary_match.start()] + raw_answer[exec_summary_match.end():]
                raw_answer = new_raw.strip() if new_raw.strip() else dynamic_summary
            else:
                paragraphs = [p.strip() for p in raw_answer.split('\n')
                              if p.strip() and not p.strip().startswith(('#', '{', '}'))]
                dynamic_summary = paragraphs[0][:247] + "..." if paragraphs and len(paragraphs[0]) > 247 else (paragraphs[0] if paragraphs else dynamic_summary)

        final_json = {
            "answer": raw_answer,
            "summary": dynamic_summary,
            "similar_cases": "",
            "sources": citations,
            "disclaimer": "This information is generated by AI based on legal documents and does not constitute professional legal advice.",
            "category": "General Legal Query"
        }

        assistant_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=json.dumps(final_json)
        )
        db.add(assistant_msg)
        db.commit()

        return KanoonQueryResponse(conversation_id=conversation.id, **final_json)


    # ─────────────────────────────────────────────────────────────────────────
    # STREAMING /query-stream endpoint (used by CivicNavigator, etc.)
    # ─────────────────────────────────────────────────────────────────────────
    async def query_stream(self, request: KanoonQueryRequest, user_id: str, db: Session, background_tasks):
        detected_lang = request.detected_lang or "en"
        language = request.language or "en"

        # Auto-detect from script — always overrides
        auto_lang = _detect_script_lang(request.question)
        if auto_lang != "en":
            detected_lang = auto_lang
            if language == "en":
                language = auto_lang

        from app.models.chat import Conversation, Message, FeatureType, MessageRole
        from app.ai.orchestrator import rag_orchestrator
        from app.services.title_service import generate_conversation_title_async

        conversation = None

        if request.conversation_id:
            from app.models.user import User
            db_user = db.query(User).filter(User.firebase_uid == user_id).first()
            target_uids = [user_id]
            if db_user:
                old_users = db.query(User).filter(User.email == db_user.email).all()
                for u in old_users:
                    target_uids.append(u.firebase_uid)

            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id.in_(target_uids)
            ).first()

            if conversation and conversation.feature_type != FeatureType.know_kanoon:
                raise HTTPException(status_code=400, detail="Conversation does not belong to Know Your Kanoon.")

        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                title="New Conversation",
                feature_type=FeatureType.know_kanoon
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            background_tasks.add_task(generate_conversation_title_async, conversation.id, request.question)

        user_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.user,
            content=request.question
        )
        db.add(user_msg)
        db.commit()

        past_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.asc()).all()
        formatted_history = [{"role": m.role.value, "content": m.content} for m in past_messages[:-1]]

        filters = {"tenant_id": "global"}

        # ── Pre-translate query concurrently ──────────────────────────────────
        if detected_lang != "en":
            from app.core.translate import translate_in as _translate_in_fn
            # Fire translate_in NOW, before we enter the generator
            translate_task = asyncio.create_task(_translate_in_fn(request.question, detected_lang))
            search_query = await translate_task
        else:
            search_query = request.question

        # Acronym expansion
        expansions = {
            "RTI": "RTI Right to Information",
            "FIR": "FIR First Information Report Police",
            "consumer forum": "consumer dispute redressal",
            "rera": "Real Estate Regulatory Authority",
        }
        for acr, exp in expansions.items():
            search_query = re.sub(rf'\b{acr}\b', exp, search_query, flags=re.IGNORECASE)

        # Capture for generator closure
        _search_query = search_query
        _language = language
        _conv = conversation
        _formatted_history = formatted_history

        async def stream_generator():
            try:
                full_content = ""
                citations_data = []

                yield f"data: {json.dumps({'type': 'metadata', 'conversation_id': _conv.id})}\n\n"

                # ── UNIFIED STREAMING PATH ────────────────────────────────────
                # Gemini now generates the correct language natively via prompting,
                # so we can stream tokens directly to the frontend regardless of language!
                for event in rag_orchestrator.trigger_pipeline_stream(
                    _search_query, filters, _formatted_history, task_type="CIVIC", language=_language
                ):
                    if event.startswith("data: "):
                        try:
                            data = json.loads(event[6:])
                            if data['type'] == 'chunk':
                                full_content += data['data']
                            elif data['type'] == 'complete':
                                citations_data = data.get('citations', [])
                            # Errors will just pass through in English for now, which is fine
                        except Exception:
                            pass
                    yield event

                # ── Save to DB ────────────────────────────────────────────────
                raw_answer = full_content
                dynamic_summary = "Response generated based on retrieved legal knowledge."
                try:
                    parsed_ans = json.loads(re.sub(r'^```(?:json)?\s*|\s*```$', '', raw_answer.strip()))
                    if "problemAndRights" in parsed_ans and "summary" in parsed_ans["problemAndRights"]:
                        dynamic_summary = parsed_ans["problemAndRights"]["summary"]
                except Exception:
                    exec_summary_match = re.search(r'(?i)##\s*Executive Summary\s*\n(.*?)(?=\n##|\Z)', raw_answer, re.DOTALL)
                    if exec_summary_match:
                        dynamic_summary = exec_summary_match.group(1).strip()
                    else:
                        paragraphs = [p.strip() for p in raw_answer.split('\n')
                                      if p.strip() and not p.strip().startswith(('#', '{', '}'))]
                        dynamic_summary = paragraphs[0] if paragraphs else dynamic_summary
                        if len(dynamic_summary) > 250:
                            dynamic_summary = dynamic_summary[:247] + "..."

                final_json = {
                    "answer": raw_answer,
                    "summary": dynamic_summary,
                    "similar_cases": "",
                    "sources": citations_data,
                    "disclaimer": "This information is generated by AI based on legal documents.",
                    "category": "General Legal Query"
                }

                assistant_msg = Message(
                    conversation_id=_conv.id,
                    role=MessageRole.assistant,
                    content=json.dumps(final_json)
                )
                db.add(assistant_msg)
                db.commit()

            except Exception as e:
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'type': 'error', 'data': f'Backend Exception: {str(e)}'})}\n\n"

        return stream_generator()


kanoon_service = KanoonService()
