"""Architect role."""

from mgx_backend.role import Role
from mgx_backend.actions import WriteDesign


class Architect(Role):
    """Architect role - designs system architecture."""
    
    name: str = "Bob"
    profile: str = "Architect"
    goal: str = "Design a concise, usable, complete software system"
    constraints: str = "Use simple architecture and appropriate open source libraries"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteDesign])
        self.watch({"WritePRD"})