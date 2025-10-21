from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.models.user import User
from app.utils.auth import get_current_user
from loguru import logger

router = APIRouter()

class WorkflowTrigger(BaseModel):
    workflow_name: str
    payload: Dict[str, Any]

class TaskWebhook(BaseModel):
    task_id: int
    title: str
    deadline: str
    priority: str
    course: Optional[str] = None
    user_email: str

class DeadlineReminder(BaseModel):
    task_id: int
    title: str
    deadline: str
    hours_remaining: int
    user_email: str

# Workflow name mapping to match your JSON files
WORKFLOW_MAPPING = {
    "new_task": "New Task Notification",
    "deadline_reminder": "Deadline Reminder",
    "daily_schedule": "Daily Schedule Generation"
}

@router.post("/trigger-workflow")
async def trigger_workflow(
    trigger: WorkflowTrigger,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger n8n workflow via webhook
    
    Available workflows:
    - new_task: Triggered when a task is created (New Task Notification)
    - deadline_reminder: Triggered for upcoming deadlines (Deadline Reminder)
    - daily_schedule: Triggered for daily schedule generation (Daily Schedule Generation)
    """
    try:
        # Map workflow name to actual n8n workflow name
        actual_workflow_name = WORKFLOW_MAPPING.get(
            trigger.workflow_name, 
            trigger.workflow_name
        )
        
        # Construct n8n webhook URL
        n8n_base_url = settings.N8N_WEBHOOK_URL or "http://localhost:5678/webhook"
        # Use the actual workflow name from JSON files
        webhook_url = f"{n8n_base_url}/{actual_workflow_name.replace(' ', '-').lower()}"
        
        logger.info(f"Triggering n8n workflow: {actual_workflow_name}")
        logger.debug(f"Webhook URL: {webhook_url}")
        logger.debug(f"Payload: {trigger.payload}")
        
        # Make request to n8n webhook
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook_url,
                json=trigger.payload
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully triggered workflow: {actual_workflow_name}")
                return {
                    "success": True,
                    "workflow": actual_workflow_name,
                    "message": "Workflow triggered successfully"
                }
            else:
                logger.error(f"n8n webhook failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail=f"n8n workflow trigger failed: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to n8n: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to n8n service: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error triggering workflow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )

@router.post("/webhooks/new-task")
async def handle_new_task_webhook(task: TaskWebhook):
    """
    Webhook endpoint for n8n to call back
    This is called BY n8n after it processes the task (New Task Notification workflow)
    """
    logger.info(f"Received callback from n8n for task: {task.task_id}")
    
    # Here you could update task status, log notifications sent, etc.
    return {
        "success": True,
        "message": f"Task {task.task_id} processed by automation"
    }

@router.post("/webhooks/deadline-reminder")
async def handle_deadline_reminder_webhook(reminder: DeadlineReminder):
    """
    Webhook endpoint for n8n to call back
    This is called BY n8n after it processes the deadline reminder
    """
    logger.info(f"Received deadline reminder callback for task: {reminder.task_id}")
    
    return {
        "success": True,
        "message": f"Deadline reminder for task {reminder.task_id} processed"
    }

@router.post("/webhooks/daily-schedule")
async def handle_daily_schedule_webhook(data: Dict[str, Any]):
    """
    Webhook endpoint for n8n to call back
    This is called BY n8n after it generates the daily schedule
    """
    logger.info(f"Received daily schedule callback for user: {data.get('user_email', 'unknown')}")
    
    return {
        "success": True,
        "message": "Daily schedule generation completed"
    }

@router.get("/workflows/status")
async def get_workflows_status():
    """
    Check if n8n is accessible and get workflow status
    """
    try:
        n8n_base_url = settings.N8N_WEBHOOK_URL or "http://localhost:5678"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to ping n8n
            response = await client.get(f"{n8n_base_url}/healthz")
            
            if response.status_code == 200:
                return {
                    "n8n_status": "online",
                    "available_workflows": {
                        "new_task": "New Task Notification",
                        "deadline_reminder": "Deadline Reminder",
                        "daily_schedule": "Daily Schedule Generation"
                    },
                    "webhook_base_url": n8n_base_url
                }
            else:
                return {
                    "n8n_status": "unhealthy",
                    "message": "n8n is running but not responding correctly"
                }
                
    except httpx.RequestError:
        return {
            "n8n_status": "offline",
            "message": "Cannot connect to n8n service",
            "check": "Ensure n8n Docker container is running on port 5678"
        }

# Helper function to trigger workflows from other routers
async def trigger_n8n_workflow(workflow_name: str, payload: Dict[str, Any]) -> bool:
    """
    Helper function to trigger n8n workflows from anywhere in the app
    
    Usage:
        from app.routers.automation import trigger_n8n_workflow
        
        # For new task notification
        success = await trigger_n8n_workflow("new_task", {
            "task_id": task.id,
            "title": task.title,
            "deadline": task.deadline,
            "priority": task.priority,
            "user_email": user.email
        })
        
        # For deadline reminder
        success = await trigger_n8n_workflow("deadline_reminder", {
            "task_id": task.id,
            "title": task.title,
            "deadline": task.deadline,
            "hours_remaining": 24,
            "user_email": user.email
        })
        
        # For daily schedule generation
        success = await trigger_n8n_workflow("daily_schedule", {
            "user_email": user.email,
            "date": "2025-10-21"
        })
    """
    try:
        # Map workflow name to actual n8n workflow name
        actual_workflow_name = WORKFLOW_MAPPING.get(workflow_name, workflow_name)
        
        n8n_base_url = settings.N8N_WEBHOOK_URL or "http://localhost:5678/webhook"
        # Use the actual workflow name with proper formatting
        webhook_url = f"{n8n_base_url}/{actual_workflow_name.replace(' ', '-').lower()}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Workflow '{actual_workflow_name}' triggered successfully")
                return True
            else:
                logger.error(f"Workflow trigger failed: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Error triggering workflow '{workflow_name}': {str(e)}")
        return False