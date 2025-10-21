from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse
from app.utils.auth import get_current_user
from app.services.rag_service import RAGService
from app.routers.automation import trigger_n8n_workflow

router = APIRouter()

rag_service = RAGService()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create task in database
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    
    # Add to RAG system for context awareness
    rag_service.add_task_to_context(current_user.id, db_task)
    
    # Trigger workflow automation (n8n)
    await trigger_n8n_workflow("new_task", {
        "task_id": db_task.id,
        "title": db_task.title,
        "deadline": str(db_task.deadline) if getattr(db_task, "deadline", None) else None,
        "priority": getattr(db_task, "priority", None),
        "user_email": current_user.email,
    })
    
    return TaskResponse.model_validate(db_task)


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)
