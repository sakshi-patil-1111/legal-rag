from fastapi import APIRouter, Depends, Request, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.rate_limit import limiter
from app.middleware.auth import verify_firebase_token, VerifiedToken
from app.schemas.upload_chat import DocumentUploadResponse, ChatQueryRequest, ChatQueryResponse
from app.services.document_service import document_service
from app.services.upload_chat_service import upload_chat_service

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
@limiter.limit("10/minute")
def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_token: VerifiedToken = Depends(verify_firebase_token),
):
    user_uid = user_token.uid
    return document_service.process_upload(user_uid, file, db)

@router.post("/query", response_model=ChatQueryResponse)
@limiter.limit("30/minute")
async def query_document(
    request: Request,
    payload: ChatQueryRequest,
    background_tasks: BackgroundTasks,
    user_token: VerifiedToken = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    try:
        response = await upload_chat_service.query(payload, db, user_token.uid, background_tasks)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
