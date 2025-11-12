"""Team management for multi-agent collaboration."""

from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field

from mgx_backend.context import Context
from mgx_backend.environment import Environment
from mgx_backend.role import Role
from mgx_backend.message import UserRequirement
from mgx_backend.cost_manager import NoMoneyException


class Team(BaseModel):
    """Team of roles working together."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    env: Optional[Environment] = None
    investment: float = 10.0
    idea: str = ""
    
    def __init__(self, context: Context = None, **data):
        super().__init__(**data)
        ctx = context or Context()
        
        if not self.env:
            self.env = Environment(context=ctx)
    
    def hire(self, roles: List[Role]):
        """Hire roles to the team."""
        self.env.add_roles(roles)
    
    def invest(self, investment: float):
        """Set investment budget."""
        self.investment = investment
        self.env.context.cost_manager.max_budget = investment
        print(f"💰 Investment: ${investment}")
    
    def _check_balance(self):
        """Check if budget is exceeded."""
        cost_manager = self.env.context.cost_manager
        if cost_manager.total_cost >= cost_manager.max_budget:
            raise NoMoneyException(
                cost_manager.total_cost,
                f"Budget exceeded: ${cost_manager.total_cost:.4f} >= ${cost_manager.max_budget:.2f}"
            )
    
    def run_project(self, idea: str):
        """Start a project with user requirement."""
        self.idea = idea
        
        # Publish user requirement
        message = UserRequirement(content=idea)
        import asyncio
        asyncio.create_task(self.env.publish_message(message))
    
    async def run(self, n_round: int = 5, idea: str = "", progress_callback=None):
        """Run the team for n rounds.
        
        Args:
            n_round: Number of rounds to run
            idea: Project idea
            progress_callback: Callback function(task_id, update_dict) for progress updates
        """
        if idea:
            self.idea = idea
            message = UserRequirement(content=idea)
            await self.env.publish_message(message)
        
        print(f"\n🚀 Starting project: {self.idea}")
        print(f"👥 Team members: {', '.join([r.name for r in self.env.get_roles()])}")
        print(f"💰 Budget: ${self.investment}\n")
        
        # Store progress callback in environment context
        if progress_callback:
            self.env.context.kwargs.set("progress_callback", progress_callback)
        
        round_num = 0
        while n_round > 0:
            if self.env.is_idle:
                print(f"\n✅ All roles are idle. Project completed!")
                break
            
            n_round -= 1
            round_num += 1
            
            print(f"--- Round {round_num} ---")
            
            # Check budget
            self._check_balance()
            
            # Run one round
            await self.env.run()
            
            # Print cost info
            cost_manager = self.env.context.cost_manager
            print(f"💵 Cost so far: ${cost_manager.total_cost:.4f} / ${cost_manager.max_budget:.2f}")
        
        print(f"\n🎉 Project completed!")
        print(f"\n{self.env.context.cost_manager.get_summary()}")
        
        return self.env.history