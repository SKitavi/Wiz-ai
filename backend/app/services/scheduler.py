"""
Background job scheduler for WizAI
Handles automated tasks like daily plan generation and deadline reminders
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from loguru import logger
import httpx

from app.database import SessionLocal
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.config import settings

# Initialize scheduler
scheduler = AsyncIOScheduler()

# ============================================================================
# Helper Functions
# ============================================================================

def get_all_users() -> List[User]:
    """
    Get all active users from database
    
    Returns:
        List of active User objects
    """
    db = SessionLocal()
    try:
        # Query all active users
        users = db.query(User).filter(User.is_active == True).all()
        logger.info(f"Found {len(users)} active users")
        return users
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        return []
    finally:
        db.close()


def get_urgent_tasks() -> List[Dict[str, Any]]:
    """
    Get tasks with deadlines in the next 24 hours
    
    Returns:
        List of task dictionaries with user information
    """
    db = SessionLocal()
    try:
        # Calculate time window (now to 24 hours from now)
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(hours=24)
        
        # Query tasks due in next 24 hours that are not completed
        urgent_tasks = db.query(Task).join(User).filter(
            Task.deadline <= tomorrow,
            Task.deadline >= now,
            Task.status != TaskStatus.COMPLETED,
            User.is_active == True
        ).all()
        
        # Convert to dictionaries with user info
        task_list = []
        for task in urgent_tasks:
            user = db.query(User).filter(User.id == task.user_id).first()
            task_dict = task.to_dict()
            task_dict['user_email'] = user.email if user else None
            task_dict['user_name'] = user.full_name if user else None
            task_list.append(task_dict)
        
        logger.info(f"Found {len(task_list)} urgent tasks")
        return task_list
        
    except Exception as e:
        logger.error(f"Failed to get urgent tasks: {e}")
        return []
    finally:
        db.close()


async def trigger_n8n_workflow(workflow_name: str, payload: Dict[str, Any]) -> bool:
    """
    Trigger an n8n workflow via webhook
    
    Args:
        workflow_name: Name of the workflow to trigger
        payload: Data to send to the workflow
        
    Returns:
        True if successful, False otherwise
    """
    # Check if n8n is configured
    if not settings.N8N_WEBHOOK_URL:
        logger.warning("N8N_WEBHOOK_URL not configured, skipping workflow trigger")
        return False
    
    # Construct webhook URL
    webhook_url = f"{settings.N8N_WEBHOOK_URL}/{workflow_name}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(webhook_url, json=payload)
            
            if response.status_code == 200:
                logger.info(f"✅ Triggered n8n workflow: {workflow_name}")
                return True
            else:
                logger.error(f"❌ n8n workflow failed: {workflow_name} (status: {response.status_code})")
                return False
                
    except Exception as e:
        logger.error(f"Failed to trigger n8n workflow {workflow_name}: {e}")
        return False


async def generate_plan_for_user(user_id: int, date: str) -> bool:
    """
    Generate a daily plan for a specific user
    
    Args:
        user_id: User ID
        date: Date in YYYY-MM-DD format
        
    Returns:
        True if successful, False otherwise
    """
    db = SessionLocal()
    try:
        # Get user's pending tasks
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == TaskStatus.PENDING
        ).order_by(Task.deadline.asc()).all()
        
        if not tasks:
            logger.info(f"No tasks for user {user_id}, skipping plan generation")
            return True
        
        # Simple plan generation logic
        # In a full implementation, this would call your planner agent
        from app.models.plan import Plan
        
        # Create schedule blocks (simplified)
        schedule = []
        current_time = datetime.strptime("09:00", "%H:%M")
        
        for task in tasks[:5]:  # Limit to 5 tasks per day
            urgency = task.calculate_urgency_score()
            duration = task.estimated_duration or 60
            
            schedule.append({
                "start_time": current_time.strftime("%H:%M"),
                "end_time": (current_time + timedelta(minutes=duration)).strftime("%H:%M"),
                "activity": task.title,
                "type": "study",
                "task_id": task.id,
                "priority": task.priority
            })
            
            # Add break
            current_time += timedelta(minutes=duration + 15)
        
        # Create or update plan
        existing_plan = db.query(Plan).filter(
            Plan.user_id == user_id,
            Plan.date == datetime.strptime(date, "%Y-%m-%d").date()
        ).first()
        
        if existing_plan:
            existing_plan.schedule = schedule
            existing_plan.schedule_summary = f"{len(schedule)} tasks scheduled"
            existing_plan.productivity_score = 85.0
        else:
            new_plan = Plan(
                user_id=user_id,
                date=datetime.strptime(date, "%Y-%m-%d").date(),
                schedule=schedule,
                schedule_summary=f"{len(schedule)} tasks scheduled",
                productivity_score=85.0
            )
            db.add(new_plan)
        
        db.commit()
        logger.info(f"✅ Generated plan for user {user_id} on {date}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate plan for user {user_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


# ============================================================================
# Scheduled Jobs
# ============================================================================

@scheduler.scheduled_job('cron', hour=6, minute=0, timezone='Africa/Nairobi')
async def daily_plan_generation():
    """
    Generate plans for all users every morning at 6 AM
    Runs daily and creates optimized schedules for each active user
    """
    logger.info("🕐 Starting daily plan generation job...")
    
    # Get all active users
    users = get_all_users()
    
    if not users:
        logger.warning("No active users found")
        return
    
    # Get today's date
    today = datetime.now(timezone.utc).date().isoformat()
    
    success_count = 0
    fail_count = 0
    
    # Generate plan for each user
    for user in users:
        try:
            # Generate plan using simplified logic
            success = await generate_plan_for_user(user.id, today)
            
            if success:
                success_count += 1
                
                # Try to trigger n8n workflow (optional)
                await trigger_n8n_workflow("daily-schedule", {
                    "user_id": user.id,
                    "user_email": user.email,
                    "date": today,
                    "event": "scheduled_daily_generation"
                })
            else:
                fail_count += 1
                
        except Exception as e:
            logger.error(f"Failed to generate plan for user {user.id}: {e}")
            fail_count += 1
    
    logger.info(f"✅ Daily plan generation completed: {success_count} success, {fail_count} failed")


@scheduler.scheduled_job('interval', hours=3, timezone='Africa/Nairobi')
async def deadline_reminders():
    """
    Check for upcoming deadlines and send reminders
    Runs every 3 hours and alerts users about tasks due within 24 hours
    """
    logger.info("⏰ Starting deadline reminder job...")
    
    # Get tasks with deadlines in next 24 hours
    urgent_tasks = get_urgent_tasks()
    
    if not urgent_tasks:
        logger.info("No urgent tasks found")
        return
    
    logger.info(f"Found {len(urgent_tasks)} urgent tasks to remind")
    
    reminder_count = 0
    
    # Send reminder for each urgent task
    for task in urgent_tasks:
        try:
            # Trigger n8n workflow for each task
            success = await trigger_n8n_workflow("deadline-reminder", {
                "task_id": task['id'],
                "task_title": task['title'],
                "deadline": task['deadline'],
                "priority": task['priority'],
                "course": task.get('course', 'N/A'),
                "user_email": task.get('user_email'),
                "user_name": task.get('user_name'),
                "event": "scheduled_deadline_reminder"
            })
            
            if success:
                reminder_count += 1
                logger.info(f"✅ Sent reminder for task: {task['title']}")
            
        except Exception as e:
            logger.error(f"Failed to send reminder for task {task['id']}: {e}")
    
    logger.info(f"✅ Deadline reminder job completed: {reminder_count}/{len(urgent_tasks)} reminders sent")


@scheduler.scheduled_job('interval', minutes=30, timezone='Africa/Nairobi')
async def sync_tasks_to_rag():
    """
    Sync all pending tasks to RAG database for context awareness
    Runs every 30 minutes to keep the vector database updated
    """
    logger.info("🔄 Starting RAG sync job...")
    
    # Only run if RAG service is available
    try:
        from app.services.rag_service import RAGService
        rag = RAGService()
    except Exception as e:
        logger.warning(f"RAG service not available, skipping sync: {e}")
        return
    
    db = SessionLocal()
    try:
        # Get all non-completed tasks
        tasks = db.query(Task).filter(
            Task.status != TaskStatus.COMPLETED
        ).all()
        
        synced_count = 0
        
        for task in tasks:
            try:
                # Add or update task in RAG
                rag.add_task_to_context(task.user_id, task.to_dict())
                synced_count += 1
            except Exception as e:
                logger.warning(f"Failed to sync task {task.id} to RAG: {e}")
        
        logger.info(f"✅ RAG sync completed: {synced_count}/{len(tasks)} tasks synced")
        
    except Exception as e:
        logger.error(f"RAG sync job failed: {e}")
    finally:
        db.close()


# ============================================================================
# Scheduler Management
# ============================================================================

def start_scheduler():
    """
    Start the background scheduler with all jobs
    Call this from main.py during app startup
    """
    try:
        scheduler.start()
        logger.info("✅ Background scheduler started successfully")
        logger.info(f"📋 Scheduled jobs: {len(scheduler.get_jobs())}")
        
        # Log all scheduled jobs
        for job in scheduler.get_jobs():
            logger.info(f"  - {job.id}: {job.name} (next run: {job.next_run_time})")
            
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        raise


def stop_scheduler():
    """
    Stop the background scheduler
    Call this during app shutdown
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("👋 Background scheduler stopped")


def get_scheduler_status() -> Dict[str, Any]:
    """
    Get current scheduler status and job information
    
    Returns:
        Dictionary with scheduler status and job details
    """
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "running": scheduler.running,
        "job_count": len(jobs),
        "jobs": jobs
    }


# ============================================================================
# Manual Job Triggers (for testing)
# ============================================================================

async def trigger_daily_plan_job():
    """Manually trigger daily plan generation (for testing)"""
    logger.info("Manually triggering daily plan generation...")
    await daily_plan_generation()


async def trigger_deadline_reminder_job():
    """Manually trigger deadline reminders (for testing)"""
    logger.info("Manually triggering deadline reminders...")
    await deadline_reminders()


async def trigger_rag_sync_job():
    """Manually trigger RAG sync (for testing)"""
    logger.info("Manually triggering RAG sync...")
    await sync_tasks_to_rag()