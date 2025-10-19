from app.agents.base_agent import BaseAgent
from langchain.tools import Tool
from typing import List, Dict, Any
from datetime import datetime, timedelta

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ScheduleMaster",
            role="Intelligent Schedule Optimizer",
            backstory="Expert at creating balanced daily schedules that maximize productivity while respecting user preferences and constraints."
        )
    def define_tools(self) -> List[Tool]:
        return [
            Tool(
                name="get_user_tasks",
                func=lambda user_id: self.mcp_server.get_user_tasks(user_id),
                description="Retrieve pending tasks for user"
            ),
            Tool(
                name="get_calendar_events",
                func=lambda user_id, date: self.mcp_server.get_calendar_events(user_id, date),
                description="Fetch calendar events for specific date"
            ),
            Tool(
                name="calculate_priority",
                func=self._calculate_priority,
                description="Calculate task priority based on deadline and importance"
            )
        ]
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized daily schedule"""
        user_id = context.get("user_id")
        target_date = context.get("date", datetime.now().date().isoformat())
        user_prefs = context.get("preferences", {})
        
        # Get tasks and calendar events via MCP
        tasks_data = await self.mcp_server.get_user_tasks(user_id, "pending")
        calendar_data = await self.mcp_server.get_calendar_events(user_id, target_date)
        
        planning_prompt = f"""
        {self.create_system_prompt()}
        
        Create an optimal schedule for {target_date}.
        
        Use chain-of-thought reasoning:
        1. Analyze all pending tasks and their deadlines
        2. Review existing calendar commitments
        3. Apply user preferences (study hours, break times)
        4. Allocate time blocks considering:
           - Task priority and urgency
           - Estimated duration
           - Optimal focus times
           - Regular breaks (every 90 minutes)
        5. Detect and resolve conflicts
        
        Tasks: {tasks_data}
        Calendar Events: {calendar_data}
        User Preferences: {user_prefs}
        
        Return JSON:
        {{
            "date": "{target_date}",
            "schedule": [
                {{"start_time": "HH:MM", "end_time": "HH:MM", "activity": "", "type": "study|break|event", "task_id": null}}
            ],
            "conflicts": [],
            "reasoning": "Explain your scheduling decisions",
            "productivity_score": 0-100
        }}
        """
        
        response = await self.llm_service.generate(planning_prompt, temperature=0.3)
        
        return {
            "success": True,
            "plan": json.loads(response),
            "agent": self.name
        }
    
    def _calculate_priority(self, task: Dict) -> int:
        """Calculate priority score"""
        deadline = datetime.fromisoformat(task['deadline'])
        days_until = (deadline - datetime.now()).days
        
        if days_until < 1:
            return 10  # Critical
        elif days_until < 3:
            return 8   # High
        elif days_until < 7:
            return 5   # Medium
        else:
            return 3   # Low
