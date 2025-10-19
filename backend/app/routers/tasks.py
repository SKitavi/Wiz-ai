from app.services.rag_service import RAGService

rag_service = RAGService()

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    # Create task in database
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    
    # Add to RAG system for context awareness
    rag_service.add_task_to_context(current_user.id, db_task)
    
    # Trigger workflow automation (n8n)
    await trigger_n8n_workflow("new_task", db_task)
    
    return db_task
