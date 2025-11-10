"""Product Manager role."""

from mgx_backend.role import Role
from mgx_backend.actions import WritePRD


class ProductManager(Role):
    """Product Manager role - writes PRD."""
    
    name: str = "Alice"
    profile: str = "Product Manager"
    goal: str = "Create a comprehensive Product Requirements Document"
    constraints: str = "Use the same language as the user requirement"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WritePRD])
        self.watch({"UserRequirement"})