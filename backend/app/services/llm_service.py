from typing import Optional, Dict, Any, List
from enum import Enum
import google.generativeai as genai
from openai import OpenAI
from app.config import settings
from loguru import logger

class ModelProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"

class LLMService:
    def __init__(self):
        # Initialize clients
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.gemini = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def generate(
        self,
        prompt: str,
        model_preference: ModelProvider = ModelProvider.GEMINI,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate response with intelligent fallback"""
        try:
            if model_preference == ModelProvider.GEMINI:
                return await self._gemini_generate(prompt, temperature, max_tokens)
            else:
                return await self._openai_generate(prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"{model_preference.value} failed: {e}, trying fallback")
            # Fallback logic
            if model_preference == ModelProvider.GEMINI:
                return await self._openai_generate(prompt, temperature, max_tokens)
            else:
                return await self._gemini_generate(prompt, temperature, max_tokens)
    
    async def _gemini_generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        response = await self.gemini.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        return response.text
    
    async def _openai_generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def route_model(self, task_type: str) -> ModelProvider:
        """Intelligent routing based on task type"""
        # Gemini for fast, structured tasks
        if task_type in ["extraction", "classification", "quick_chat"]:
            return ModelProvider.GEMINI
        # OpenAI for complex reasoning
        elif task_type in ["planning", "analysis", "creative"]:
            return ModelProvider.OPENAI
        return ModelProvider.GEMINI  # Default