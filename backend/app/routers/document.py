from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService, ModelProvider
from app.schemas.document import DocumentResponse
import aiofiles  # pyright: ignore[reportMissingModuleSource]
from pathlib import Path
import uuid

router = APIRouter()
ocr_service = OCRService()
llm_service = LLMService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document (PDF, image, DOCX)"""
    # Validate file type
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Unsupported file type")
    
    # Save file temporarily
    file_id = str(uuid.uuid4())
    file_path = Path(f"./uploads/{file_id}_{file.filename}")
    file_path.parent.mkdir(exist_ok=True)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    # Extract text based on file type
    try:
        if file.content_type == "application/pdf":
            text = ocr_service.extract_from_pdf(str(file_path))
        elif file.content_type in ["image/png", "image/jpeg"]:
            text = ocr_service.extract_from_image(str(file_path))
        else:
            text = ocr_service.extract_from_docx(str(file_path))
        
        # Use LLM to extract structured info
        extraction_prompt = f"""
        Extract assignments, deadlines, and events from this text.
        Return JSON with format:
        {{
            "assignments": [
                {{"title": "...", "deadline": "YYYY-MM-DD", "course": "...", "description": "..."}}
            ],
            "events": [
                {{"title": "...", "date": "YYYY-MM-DD", "time": "HH:MM", "location": "..."}}
            ]
        }}
Text:
        {text[:4000]}  # Truncate for token limits
        """
        
        structured_data = await llm_service.generate(extraction_prompt, model_preference=ModelProvider.GEMINI)
        
        return {
            "document_id": file_id,
            "filename": file.filename,
            "extracted_text": text[:500],  # Preview
            "structured_data": structured_data
        }
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")
