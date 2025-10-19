from typing import Dict, Any, List
from app.agents.extraction_agent import ExtractionAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.chat_agent import ChatAgent
from loguru import logger

class AgentCoordinator:
    def __init__(self):
        self.extraction_agent = ExtractionAgent()
        self.planner_agent = PlannerAgent()
        self.chat_agent = ChatAgent()
        
        logger.info("Agent coordinator initialized with 3 specialized agents")
    
    async def process_document(self, user_id: int, document_text: str) -> Dict[str, Any]:
        """Coordinate document processing workflow"""
        logger.info(f"Starting document processing workflow for user {user_id}")
        
        # Step 1: Extraction Agent extracts structured data
        extraction_result = await self.extraction_agent.execute(
            task="extract_information",
            context={"document_text": document_text}
        )
        
        if not extraction_result["success"]:
            return {"success": False, "error": "Extraction failed"}
        
        # Step 2: Store extracted tasks in database and RAG
        extracted_data = extraction_result["data"]
        tasks_created = []
        
        for assignment in extracted_data.get("assignments", []):
            # Create task in DB (simplified)
            task_id = await self._create_task(user_id, assignment)
            tasks_created.append(task_id)
        
        # Step 3: Trigger Planner Agent to update schedule
        plan_result = await self.planner_agent.execute(
            task="generate_plan",
            context={
                "user_id": user_id,
                "date": datetime.now().date().isoformat()
            }
        )
        
        return {
            "success": True,
            "tasks_created": len(tasks_created),
            "extraction": extraction_result,
            "plan_updated": plan_result["success"],
            "workflow": "document -> extraction -> planning"
        }
    async def handle_chat(self, user_id: int, message: str, chat_history: List[Dict]) -> Dict[str, Any]:
        """Route chat to appropriate agent"""
        
        # Determine if this requires planning
        intent = await self._classify_intent(message)
        
        if intent == "schedule_query" or intent == "schedule_modification":
            # May need planner agent
            chat_result = await self.chat_agent.execute(
                task="respond",
                context={
                    "user_id": user_id,
                    "message": message,
                    "chat_history": chat_history
                }
            )
            
            # If schedule modification detected, trigger planner
            if "modify" in message.lower() or "move" in message.lower():
                await self.planner_agent.execute(
                    task="adjust_plan",
                    context={"user_id": user_id, "modification": message}
                )
            
            return chat_result
        else:
            # Simple chat response
            return await self.chat_agent.execute(
                task="respond",
                context={"user_id": user_id, "message": message, "chat_history": chat_history}
            )
    async def _classify_intent(self, message: str) -> str:
        """Classify user intent"""
        # Simple keyword-based classification
        if any(word in message.lower() for word in ["schedule", "plan", "today", "tomorrow"]):
            return "schedule_query"
        elif any(word in message.lower() for word in ["move", "change", "reschedule"]):
            return "schedule_modification"
        else:
            return "general_chat"
    
    async def _create_task(self, user_id: int, assignment: Dict) -> int:
        """Helper to create task"""
        # Implementation
        pass
