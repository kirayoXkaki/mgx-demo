"""Cost management for LLM API calls."""

from typing import ClassVar
from pydantic import BaseModel, Field


class CostManager(BaseModel):
    """Manage and track API call costs."""
    
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost: float = 0.0
    max_budget: float = 10.0
    
    # Pricing per 1K tokens (as of 2024)
    PRICING: ClassVar[dict] = {
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    }
    
    def update_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str
    ):
        """Update cost based on token usage."""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        
        # Get pricing for model
        pricing = self.PRICING.get(model, self.PRICING["gpt-4-turbo"])
        
        # Calculate cost (price is per 1K tokens)
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        
        self.total_cost += prompt_cost + completion_cost
    
    def check_budget(self):
        """Check if budget is exceeded."""
        if self.total_cost >= self.max_budget:
            raise NoMoneyException(
                self.total_cost,
                f"Budget exceeded: ${self.total_cost:.4f} >= ${self.max_budget:.2f}"
            )
    
    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self.total_prompt_tokens + self.total_completion_tokens
    
    def get_summary(self) -> str:
        """Get cost summary."""
        return (
            f"Cost Summary:\n"
            f"  Prompt tokens: {self.total_prompt_tokens:,}\n"
            f"  Completion tokens: {self.total_completion_tokens:,}\n"
            f"  Total tokens: {self.total_tokens:,}\n"
            f"  Total cost: ${self.total_cost:.4f}\n"
            f"  Budget: ${self.max_budget:.2f}\n"
            f"  Remaining: ${max(0, self.max_budget - self.total_cost):.4f}"
        )


class NoMoneyException(Exception):
    """Exception raised when budget is exceeded."""
    
    def __init__(self, cost: float, message: str):
        self.cost = cost
        super().__init__(message)