from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    """Uploaded document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Local storage path
    file_type = Column(String, nullable=False)  # pdf, png, jpg, docx
    file_size = Column(Integer, nullable=True)  # bytes
    
    # Extraction results
    extracted_text = Column(Text, nullable=True)  # Raw OCR/PDF text
    processed_data = Column(JSON, nullable=True)  # Structured extraction results
    # Format: {
    #   "assignments": [...],
    #   "events": [...],
    #   "confidence": 0.95
    # }
    
    # Processing status
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # ChromaDB integration
    chromadb_id = Column(String, nullable=True)  # Vector DB document ID
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "extracted_text": self.extracted_text[:500] if self.extracted_text else None,  # Preview
            "processed_data": self.processed_data,
            "processing_status": self.processing_status,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
