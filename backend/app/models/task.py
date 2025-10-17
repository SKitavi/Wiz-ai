from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, enum.Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(Base):
    """Task/Assignment model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Task details
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    course = Column(String, nullable=True)
    
    # Scheduling
    deadline = Column(DateTime(timezone=True), nullable=False, index=True)
    estimated_duration = Column(Integer, default=60)  # minutes
    
    # Status and priority
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, index=True)
    
    # Source tracking
    source = Column(String, nullable=True)  # "manual", "document", "portal", "calendar"
    source_id = Column(String, nullable=True)  # ID from source system
    
    # Integration IDs
    calendar_event_id = Column(String, nullable=True)  # Google Calendar event ID
    chromadb_id = Column(String, nullable=True)  # Vector DB document ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    
    def to_dict(self):
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "course": self.course,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "estimated_duration": self.estimated_duration,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def calculate_urgency_score(self) -> int:
        """Calculate urgency score (0-10) based on deadline and priority"""
        from datetime import datetime, timezone
        
        if self.status == TaskStatus.COMPLETED:
            return 0
        
        # Days until deadline
        now = datetime.now(timezone.utc)
        time_diff = self.deadline - now
        days_until = time_diff.days
        
        # Base score from priority
        priority_scores = {
            TaskPriority.LOW: 2,
            TaskPriority.MEDIUM: 5,
            TaskPriority.HIGH: 8,
            TaskPriority.URGENT: 10
        }
        base_score = priority_scores.get(self.priority, 5)
        
        # Adjust based on deadline proximity
        if days_until < 0:  # Overdue
            return 10
        elif days_until == 0:  # Due today
            return max(base_score, 9)
        elif days_until == 1:  # Due tomorrow
            return max(base_score, 7)
        elif days_until <= 3:  # Due within 3 days
            return max(base_score, 6)
        else:
            return base_score
