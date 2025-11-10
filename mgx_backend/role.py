"""Base role class."""

from typing import List, Set, Optional, Any
from pydantic import BaseModel, ConfigDict, Field

from mgx_backend.action import Action
from mgx_backend.message import Message
from mgx_backend.llm import BaseLLM


class Role(BaseModel):
    """Base class for all roles."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "Role"
    profile: str = "Role"
    goal: str = ""
    constraints: str = ""
    
    actions: List[Action] = Field(default_factory=list)
    _watch: Set[str] = Field(default_factory=set)
    _env: Optional[Any] = None
    _llm: Optional[BaseLLM] = None
    
    _news: List[Message] = Field(default_factory=list)
    _todo: Optional[Action] = None
    
    def set_actions(self, actions: List[type]):
        """Set actions for this role."""
        self.actions = [action() for action in actions]
    
    def set_env(self, env: Any):
        """Set environment."""
        self._env = env
        self._llm = env.context.llm()
        
        # Set LLM for all actions
        for action in self.actions:
            action.set_llm(self._llm)
    
    def watch(self, action_types: Set[str]):
        """Watch for specific action types."""
        self._watch = action_types
    
    async def observe(self, message: Message):
        """Observe a message."""
        # Check if this role should react to this message
        if not self._watch or message.cause_by in self._watch:
            self._news.append(message)
    
    @property
    def is_idle(self) -> bool:
        """Check if role is idle."""
        return len(self._news) == 0 and self._todo is None
    
    async def think(self) -> bool:
        """Decide what to do next."""
        if not self._news:
            return False
        
        # Simple strategy: execute actions in order
        if self.actions:
            self._todo = self.actions[0]
            return True
        
        return False
    
    async def act(self) -> Message:
        """Execute current action."""
        if not self._todo:
            return None
        
        # Get context from news
        context = "\n".join([msg.content for msg in self._news])
        
        # Execute action
        result = await self._todo.run(context)
        
        # Create output message
        message = Message(
            content=result,
            role=self.name,
            cause_by=self._todo.name,
            sent_from=self.name
        )
        
        # Clear news and todo
        self._news = []
        self._todo = None
        
        return message
    
    async def run(self) -> Optional[Message]:
        """Run the role (think + act)."""
        if await self.think():
            message = await self.act()
            if message and self._env:
                await self._env.publish_message(message)
            return message
        return None