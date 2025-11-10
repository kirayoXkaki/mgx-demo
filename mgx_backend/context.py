"""Global context for MGX Backend."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from mgx_backend.config import Config
from mgx_backend.cost_manager import CostManager
from mgx_backend.llm import BaseLLM, OpenAILLM


class AttrDict(BaseModel):
    """A dict-like object that allows access to keys as attributes."""
    
    model_config = ConfigDict(extra="allow")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__.update(kwargs)
    
    def __getattr__(self, key):
        return self.__dict__.get(key, None)
    
    def __setattr__(self, key, value):
        self.__dict__[key] = value
    
    def set(self, key, val: Any):
        self.__dict__[key] = val
    
    def get(self, key, default: Any = None):
        return self.__dict__.get(key, default)


class Context(BaseModel):
    """Global context for the MGX system."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    kwargs: AttrDict = Field(default_factory=AttrDict)
    config: Config = Field(default_factory=Config.default)
    cost_manager: CostManager = Field(default_factory=CostManager)
    
    _llm: Optional[BaseLLM] = None
    
    def llm(self) -> BaseLLM:
        """Get or create LLM instance."""
        if self._llm is None:
            self._llm = OpenAILLM(
                api_key=self.config.llm.api_key,
                model=self.config.llm.model,
                base_url=self.config.llm.base_url,
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens,
            )
            self._llm.cost_manager = self.cost_manager
        return self._llm
    
    @property
    def project_path(self) -> str:
        """Get project path."""
        return self.kwargs.get("project_path", self.config.project.project_path)
    
    @project_path.setter
    def project_path(self, value: str):
        """Set project path."""
        self.kwargs.set("project_path", value)
        self.config.project.project_path = value