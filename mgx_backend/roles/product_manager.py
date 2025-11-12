"""Product Manager role."""

from mgx_backend.role import Role
from mgx_backend.actions.write_prd import WritePRD


class ProductManager(Role):
    """Product Manager role - writes PRD."""
    
    name: str = "Alice"
    profile: str = "Product Manager"
    goal: str = "Write comprehensive Product Requirements Document"
    constraints: str = "Follow standard PRD format"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.set_actions([WritePRD])
        self.watch({"UserRequirement"})
    
    def set_actions(self, actions):
        """Set actions for this role."""
        self.actions = [action() for action in actions]
    
    def watch(self, action_types):
        """Watch for specific action types."""
        self._watch = action_types