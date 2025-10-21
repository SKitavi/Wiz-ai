from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course: Optional[str] = None
    deadline: datetime
    estimated_duration: Optional[int] = Field(default=60, ge=1)
    priority: Optional[str] = "medium"

class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    course: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


