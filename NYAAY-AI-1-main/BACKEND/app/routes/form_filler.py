from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import io
from app.services.form_filler_service import form_filler_service
from app.middleware.auth import verify_firebase_token, VerifiedToken
from app.core.rate_limit import limiter
from fastapi import Request
from app.utils.document_generators import DocumentGenerator

router = APIRouter()

class StartSessionRequest(BaseModel):
    form_id: str
    language: Optional[str] = "en"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    form_id: str
    collected_fields: Dict[str, str]
    user_answer: str
    history: List[ChatMessage]
    language: Optional[str] = "en"
    detected_lang: Optional[str] = "en"

class DownloadRequest(BaseModel):
    content: str

@router.post("/start")
@limiter.limit("10/minute")
async def start_session(
    request: Request,
    payload: StartSessionRequest,
    user_token: VerifiedToken = Depends(verify_firebase_token)
):
    try:
        from app.core.translate import translate_out
        response = form_filler_service.start_session(payload.form_id)
        if payload.language and payload.language != "en":
            response["question"], _ = await translate_out(response["question"], payload.language)
            if "explanation" in response:
                response["explanation"], _ = await translate_out(response["explanation"], payload.language)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/chat")
@limiter.limit("20/minute")
async def chat(
    request: Request,
    payload: ChatRequest,
    user_token: VerifiedToken = Depends(verify_firebase_token)
):
    try:
        from app.core.translate import translate_in, translate_out
        user_answer = payload.user_answer
        detected_lang = payload.detected_lang or "en"
        language = payload.language or "en"

        if detected_lang != "en":
            user_answer = await translate_in(user_answer, detected_lang)

        history_dicts = [{"role": msg.role, "content": msg.content} for msg in payload.history]
        response = form_filler_service.process_answer(
            form_id=payload.form_id,
            collected_fields=payload.collected_fields,
            user_answer=user_answer,
            history=history_dicts
        )
        
        if language != "en":
            if "question" in response:
                response["question"], _ = await translate_out(response["question"], language)
            if "explanation" in response:
                response["explanation"], _ = await translate_out(response["explanation"], language)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/pdf")
def download_pdf(
    payload: DownloadRequest,
    user_token: VerifiedToken = Depends(verify_firebase_token)
):
    try:
        pdf_buffer = DocumentGenerator.generate_reasoning_pdf(payload.content)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]), 
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=form_document.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.post("/download/docx")
def download_docx(
    payload: DownloadRequest,
    user_token: VerifiedToken = Depends(verify_firebase_token)
):
    try:
        docx_buffer = DocumentGenerator.generate_text_docx(payload.content)
        return StreamingResponse(
            iter([docx_buffer.getvalue()]), 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
            headers={"Content-Disposition": "attachment; filename=form_document.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(e)}")

@router.get("/templates/{form_id}")
def get_template(
    form_id: str,
    user_token: VerifiedToken = Depends(verify_firebase_token)
):
    try:
        return form_filler_service.get_template(form_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
