from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Any
from app.services.rag_service import RAGService
from app.models.task import Task
from app.database import SessionLocal

class WizAIMCPServer:
    def __init__(self):
        self.server = Server("wizai-mcp")
        self.rag = RAGService()
        self.db = SessionLocal()
        
        # Register tools
        self.register_tools()
    
    def register_tools(self):
        """Register MCP tools for agents"""
        
        @self.server.tool()
        async def get_user_tasks(user_id: int, status: str = "pending") -> dict:
            """Retrieve user tasks from database"""
            tasks = self.db.query(Task).filter(
                Task.user_id == user_id,
                Task.status == status
            ).all()
            return {"tasks": [task.to_dict() for task in tasks]}
        
        @self.server.tool()
        async def search_context(user_id: int, query: str) -> dict:
            """Semantic search in user context"""
            results = self.rag.query(user_id, query, top_k=3)
            return {"results": results}
        @self.server.tool()
        async def update_task_status(task_id: int, new_status: str) -> dict:
            """Update task status"""
            task = self.db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = new_status
                self.db.commit()
                return {"success": True, "task": task.to_dict()}
            return {"success": False, "error": "Task not found"}
        
        @self.server.tool()
        async def get_calendar_events(user_id: int, date: str) -> dict:
            """Fetch Google Calendar events for date"""
            from app.services.calendar_sync import CalendarService
            cal_service = CalendarService()
            events = await cal_service.get_events_for_date(user_id, date)
            return {"events": events}
