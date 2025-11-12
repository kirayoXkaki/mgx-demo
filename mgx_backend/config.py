"""Configuration management for MGX Backend."""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
import yaml


class LLMConfig(BaseModel):
    """LLM configuration."""
    api_type: str = "openai"
    model: str = "gpt-4-turbo"
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class ProjectConfig(BaseModel):
    """Project configuration."""
    workspace: str = "./workspace"
    project_name: str = ""
    project_path: str = ""


class Config(BaseModel):
    """Main configuration class."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    
    @classmethod
    def default(cls) -> "Config":
        """Create default configuration with environment variables."""
        config = cls()
        
        # Load from environment variables
        if api_key := os.getenv("OPENAI_API_KEY"):
            config.llm.api_key = api_key
        if model := os.getenv("OPENAI_MODEL"):
            config.llm.model = model
        if base_url := os.getenv("OPENAI_BASE_URL"):
            config.llm.base_url = base_url
        if workspace := os.getenv("MGX_WORKSPACE"):
            config.project.workspace = workspace
            
        return config
    
    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    def update_project(
        self,
        project_path: str = "",
        project_name: str = "",
    ):
        """Update project configuration."""
        if project_path:
            self.project.project_path = project_path
        if project_name:
            self.project.project_name = project_name
        
        # Set default project path if not provided
        if not self.project.project_path:
            workspace = Path(self.project.workspace)
            workspace.mkdir(parents=True, exist_ok=True)
            
            if self.project.project_name:
                self.project.project_path = str(workspace / self.project.project_name)
            else:
                # Generate unique project name
                import time
                timestamp = int(time.time())
                self.project.project_path = str(workspace / f"project_{timestamp}")