"""Message schema for role communication."""

from typing import Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    """Message passed between roles."""
    
    content: str
    role: str = "user"
    cause_by: str = ""
    sent_from: str = ""
    send_to: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"[{self.role}] {self.content[:100]}..."
    
    def __repr__(self) -> str:
        return self.__str__()


class UserRequirement(Message):
    """User requirement message."""
    
    def __init__(self, content: str, **kwargs):
        super().__init__(
            content=content,
            role="User",
            cause_by="UserRequirement",
            **kwargs
        )