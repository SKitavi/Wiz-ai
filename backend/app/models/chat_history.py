from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ChatHistory(Base):
    """Chat conversation history model"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message details
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    
    # Context and metadata
    context_used = Column(JSON, nullable=True)  # Which documents/tasks were retrieved
    # Format: {
    #   "retrieved_docs": [{"id": "doc_123", "relevance": 0.89}],
    #   "model_used": "gemini-2.0-flash",
    #   "tokens": 350
    # }
    
    # Agent information
    agent_name = Column(String, nullable=True)  # Which agent handled this
    
    # Session grouping
    session_id = Column(String, nullable=True, index=True)  # Group related conversations
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    
    def to_dict(self):
        """Convert chat message to dictionary"""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "context_used": self.context_used,
            "agent_name": self.agent_name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
