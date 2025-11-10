"""Environment for role communication."""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from mgx_backend.message import Message
from mgx_backend.context import Context


class Environment(BaseModel):
    """Environment for role communication (message bus)."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    context: Context
    roles: Dict[str, Any] = Field(default_factory=dict)
    history: List[Message] = Field(default_factory=list)
    
    def add_roles(self, roles: List[Any]):
        """Add roles to environment."""
        for role in roles:
            self.roles[role.name] = role
            role.set_env(self)
    
    async def publish_message(self, message: Message):
        """Publish message to all roles."""
        self.history.append(message)
        
        # Notify all roles about the new message
        for role in self.roles.values():
            await role.observe(message)
    
    def get_roles(self) -> List[Any]:
        """Get all roles."""
        return list(self.roles.values())
    
    @property
    def is_idle(self) -> bool:
        """Check if all roles are idle."""
        return all(role.is_idle for role in self.roles.values())
    
    async def run(self):
        """Run one round of role execution."""
        for role in self.roles.values():
            if not role.is_idle:
                await role.run()


# Avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mgx_backend.role import Role
else:
    Any = object