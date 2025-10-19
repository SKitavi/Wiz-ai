from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from app.services.llm_service import LLMService
from app.mcp.server import WizAIMCPServer
from loguru import logger

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, backstory: str):
        self.name = name
        self.role = role
        self.backstory = backstory
        self.llm_service = LLMService()
        self.mcp_server = WizAIMCPServer()
        self.memory = ConversationBufferMemory(return_messages=True)
        self.tools = self.define_tools()
        
        logger.info(f"Initialized {self.name} agent with role: {self.role}")
    
    @abstractmethod
    def define_tools(self) -> List[Any]:
        """Define agent-specific tools"""
        pass
    
    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent's primary task"""
        pass
    def create_system_prompt(self) -> str:
        """Generate system prompt for agent"""
        return f"""
        You are {self.name}, a specialized AI agent.
        
        Role: {self.role}
        Backstory: {self.backstory}
        
        Your capabilities:
        - Access to specific tools for your domain
        - Ability to reason and make decisions
        - Coordination with other agents when needed
        
        Always explain your reasoning and actions clearly.
        """

