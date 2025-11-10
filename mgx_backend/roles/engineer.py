"""Engineer role."""

from mgx_backend.role import Role
from mgx_backend.actions.write_code import WriteCode


class Engineer(Role):
    """Engineer role - implements code."""
    
    name: str = "Charlie"
    profile: str = "Engineer"
    goal: str = "Implement working code"
    constraints: str = "Write clean, maintainable code"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.set_actions([WriteCode])
        self.watch({"WriteDesign"})
    
    def set_actions(self, actions):
        """Set actions for this role."""
        self.actions = [action() for action in actions]
    
    def watch(self, action_types):
        """Watch for specific action types."""
        self._watch = action_types