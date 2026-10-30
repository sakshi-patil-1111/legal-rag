from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.services.reasoning_service import reasoning_service, ReasoningRequest
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.responses import StreamingResponse
from app.utils.document_generators import DocumentGenerator
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.middleware.auth import verify_firebase_token, VerifiedToken

router = APIRouter()

class ReasoningResponse(BaseModel):
    conversation_id: str
    analysis_id: str
    content: str
    citations: List[Dict[str, Any]]
    created_at: str

@router.post("/generate", response_model=ReasoningResponse)
async def generate_analysis(
    request: ReasoningRequest,
    background_tasks: BackgroundTasks,
    user_token: VerifiedToken = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    try:
        response = await reasoning_service.generate_analysis(request, user_token.uid, db, background_tasks)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class ReasoningPDFRequest(BaseModel):
    content: str

@router.post("/download/pdf")
def download_reasoning_pdf(request: ReasoningPDFRequest):
    try:
        pdf_buffer = DocumentGenerator.generate_reasoning_pdf(request.content)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Legal_Reasoning.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
