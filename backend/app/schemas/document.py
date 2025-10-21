from pydantic import BaseModel
from typing import Optional, Any


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    extracted_text: Optional[str] = None
    structured_data: Optional[Any] = None


