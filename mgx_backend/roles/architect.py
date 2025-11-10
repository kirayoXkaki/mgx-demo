"""Architect role."""

from mgx_backend.role import Role
from mgx_backend.actions.write_design import WriteDesign


class Architect(Role):
    """Architect role - designs system architecture."""
    
    name: str = "Bob"
    profile: str = "Architect"
    goal: str = "Design system architecture"
    constraints: str = "Follow best practices"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.set_actions([WriteDesign])
        self.watch({"WritePRD"})
    
    def set_actions(self, actions):
        """Set actions for this role."""
        self.actions = [action() for action in actions]
    
    def watch(self, action_types):
        """Watch for specific action types."""
        self._watch = action_types