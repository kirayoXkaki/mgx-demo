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
        system_prompt: Optional[str] = None,
        stream_callback: Optional[callable] = None
    ) -> str:
        """Ask OpenAI a question.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            stream_callback: Optional callback function(chunk: str) for streaming
        """
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
            # Use streaming if callback is provided
            if stream_callback:
                stream = await self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True,
                )
                
                full_content = ""
                prompt_tokens_estimate = sum(len(msg["content"].split()) * 1.3 for msg in messages)  # Rough estimate
                completion_tokens = 0
                
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        completion_tokens += len(content.split())  # Rough token estimate
                        if stream_callback:
                            await stream_callback(content)
                    
                    # Get usage from final chunk if available
                    if chunk.usage:
                        prompt_tokens_estimate = chunk.usage.prompt_tokens
                        completion_tokens = chunk.usage.completion_tokens
                
                # Update cost with estimated tokens
                if self.cost_manager:
                    self.cost_manager.update_cost(
                        prompt_tokens=int(prompt_tokens_estimate),
                        completion_tokens=int(completion_tokens),
                        model=self.model
                    )
                    self.cost_manager.check_budget()
                
                return full_content
            else:
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