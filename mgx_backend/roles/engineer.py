"""Engineer role."""

from mgx_backend.role import Role
from mgx_backend.actions import WriteCode


class Engineer(Role):
    """Engineer role - writes code."""
    
    name: str = "Charlie"
    profile: str = "Engineer"
    goal: str = "Write clean, efficient, production-ready code"
    constraints: str = "Follow best practices and coding standards"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteCode])
        self.watch({"WriteDesign"})