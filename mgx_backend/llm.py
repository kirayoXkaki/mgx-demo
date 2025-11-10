"""LLM wrapper for OpenAI API."""

import asyncio
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
from openai import AsyncOpenAI

from mgx_backend.cost_manager import CostManager


class BaseLLM(BaseModel):
    """Base class for LLM providers."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    cost_manager: Optional[CostManager] = None
    
    async def ask(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Ask LLM a question."""
        raise NotImplementedError


class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation."""
    
    api_key: str
    model: str = "gpt-4-turbo"
    base_url: str = "https://api.openai.com/v1"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    _client: Optional[AsyncOpenAI] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Ask OpenAI a question."""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            # Update cost
            if self.cost_manager:
                usage = response.usage
                self.cost_manager.update_cost(
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    model=self.model
                )
                self.cost_manager.check_budget()
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {str(e)}")
    
    async def ask_batch(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None
    ) -> List[str]:
        """Ask multiple questions in parallel."""
        tasks = [self.ask(prompt, system_prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)