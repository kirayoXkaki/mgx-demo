"""
MGX Backend - Simplified MetaGPT Implementation

A multi-agent system for automated software development.
"""

__version__ = "0.1.0"

from mgx_backend.software_company import generate_repo
from mgx_backend.project_repo import ProjectRepo
from mgx_backend.config import Config
from mgx_backend.context import Context

__all__ = [
    "generate_repo",
    "ProjectRepo",
    "Config",
    "Context",
]