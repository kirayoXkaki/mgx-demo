"""Base action class."""

from typing import Optional
from pydantic import BaseModel, ConfigDict

from mgx_backend.llm import BaseLLM


class Action(BaseModel):
    """Base class for all actions."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "Action"
    llm: Optional[BaseLLM] = None
    
    def set_llm(self, llm: BaseLLM):
        """Set LLM instance."""
        self.llm = llm
    
    async def run(self, context: str, stream_callback: Optional[callable] = None) -> str:
        """Execute the action.
        
        Args:
            context: Context for the action
            stream_callback: Optional callback function(chunk: str) for streaming output
        """
        raise NotImplementedError
    
    def build_prompt(self, context: str, **kwargs) -> str:
        """Build prompt for LLM."""
        raise NotImplementedError