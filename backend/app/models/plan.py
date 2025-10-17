from sqlalchemy import Column, Integer, String, DateTime, Date, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Plan(Base):
    """Daily plan model"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Plan details
    date = Column(Date, nullable=False, index=True)
    
    # Schedule stored as JSON array
    schedule = Column(JSON, nullable=False, default=[])
    # Format: [
    #   {
    #     "start_time": "09:00",
    #     "end_time": "10:30",
    #     "activity": "Math homework",
    #     "type": "study",  # study, break, event, personal
    #     "task_id": 123,
    #     "priority": "high"
    #   }
    # ]
    
    # Summary for quick display
    schedule_summary = Column(String, nullable=True)  # "3 study blocks, 2 breaks, 1 event"
    
    # AI reasoning and metadata
    reasoning = Column(JSON, nullable=True)  # Why the AI scheduled things this way
    productivity_score = Column(Float, nullable=True)  # 0-100 AI-estimated productivity
    
    # Conflicts and warnings
    conflicts = Column(JSON, default=[])  # List of detected conflicts
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="plans")
    
    def to_dict(self):
        """Convert plan to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat() if self.date else None,
            "schedule": self.schedule,
            "schedule_summary": self.schedule_summary,
            "reasoning": self.reasoning,
            "productivity_score": self.productivity_score,
            "conflicts": self.conflicts,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
