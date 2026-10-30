from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.ai.drafting_orchestrator import drafting_orchestrator
from app.schemas.drafting import StructuredDocumentObject
from app.utils.document_generators import DocumentGenerator
from app.middleware.auth import VerifiedToken, verify_firebase_token
from app.core.rate_limit import limiter

router = APIRouter()

class DraftRequest(BaseModel):
    user_facts: str
    provided_fields: Optional[Dict[str, str]] = None
    language: Optional[str] = "en"
    detected_lang: Optional[str] = "en"

class EditRequest(BaseModel):
    document_object: StructuredDocumentObject
    edit_instructions: str
    language: Optional[str] = "en"
    detected_lang: Optional[str] = "en"

@router.post("/generate")
@limiter.limit("10/minute")
async def generate_draft(request: Request, payload: DraftRequest, _: VerifiedToken = Depends(verify_firebase_token)):
    try:
        from app.core.translate import translate_in, translate_out
        
        detected_lang = payload.detected_lang or "en"
        language = payload.language or "en"
        
        user_facts = payload.user_facts
        provided_fields = payload.provided_fields
        
        if detected_lang != "en":
            user_facts = await translate_in(user_facts, detected_lang)
            if provided_fields:
                for k, v in provided_fields.items():
                    provided_fields[k] = await translate_in(v, detected_lang)
                    
        response = drafting_orchestrator.trigger_drafting_pipeline(user_facts, provided_fields)
        
        if language != "en":
            if response.get("status") == "ERROR" and "message" in response:
                response["message"], _ = await translate_out(response["message"], language)
            elif response.get("status") == "MISSING_INFO" and "missing_fields" in response:
                translated_fields = []
                for field in response["missing_fields"]:
                    translated, _ = await translate_out(field, language)
                    translated_fields.append(translated)
                response["missing_fields"] = translated_fields
                
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit", response_model=StructuredDocumentObject)
@limiter.limit("20/minute")
async def edit_draft(request: Request, payload: EditRequest, _: VerifiedToken = Depends(verify_firebase_token)):
    try:
        from app.core.translate import translate_in
        
        detected_lang = payload.detected_lang or "en"
        edit_instructions = payload.edit_instructions
        
        if detected_lang != "en":
            edit_instructions = await translate_in(edit_instructions, detected_lang)
            
        updated_doc = drafting_orchestrator.edit_document_object(
            payload.document_object.model_dump(),
            edit_instructions
        )
        # Manually increment version
        updated_doc.metadata.version = payload.document_object.metadata.version + 1
        return updated_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/pdf")
@limiter.limit("30/minute")
def download_pdf(request: Request, doc_obj: StructuredDocumentObject, _: VerifiedToken = Depends(verify_firebase_token)):
    try:
        buffer = DocumentGenerator.generate_pdf(doc_obj)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={doc_obj.document_type.lower()}_draft.pdf"}
        )
    except Exception as e:
        import traceback
        import logging
        logging.getLogger(__name__).error(f"PDF Export Failed:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": "Failed to generate PDF", "reason": str(e)})

@router.post("/download/docx")
@limiter.limit("30/minute")
def download_docx(request: Request, doc_obj: StructuredDocumentObject, _: VerifiedToken = Depends(verify_firebase_token)):
    try:
        buffer = DocumentGenerator.generate_docx(doc_obj)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={doc_obj.document_type.lower()}_draft.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
