from app.agents.base_agent import BaseAgent
from langchain.tools import Tool
from typing import List, Dict, Any

class ChatAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ConversationalAssistant",
            role="Context-Aware Chat Interface",
            backstory="Friendly assistant that helps users interact with their schedule, answer questions, and modify plans through natural language."
        )
    
    def define_tools(self) -> List[Tool]:
        return [
            Tool(
                name="search_user_context",
                func=lambda user_id, query: self.mcp_server.search_context(user_id, query),
                description="Search user's tasks and plans for relevant information"
            ),
            Tool(
                name="modify_schedule",
                func=self._modify_schedule,
                description="Adjust user's schedule based on natural language request"
            )
        ]
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process conversational query with full context"""
        user_id = context.get("user_id")
        user_message = context.get("message")
        chat_history = context.get("chat_history", [])
        
        # Retrieve relevant context via MCP
        relevant_context = await self.mcp_server.search_context(user_id, user_message)
        
        chat_prompt = f"""
        {self.create_system_prompt()}
        
        User Context (from RAG):
        {relevant_context}
        
        Conversation History:
        {self._format_chat_history(chat_history)}
        
        User Message: {user_message}
        
        Provide a helpful, context-aware response. If the user wants to modify their schedule or tasks, use the available tools to make changes.
        """
        
        response = await self.llm_service.generate(chat_prompt)
        
        return {
            "success": True,
            "response": response,
            "agent": self.name,
            "context_used": len(relevant_context.get("results", []))
        }
    def _format_chat_history(self, history: List[Dict]) -> str:
        formatted = []
        for msg in history[-5:]:  # Last 5 messages
            formatted.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(formatted)
    
    def _modify_schedule(self, modification: str) -> str:
        """Tool for schedule modifications"""
        # Implementation
        pass
