"""Load configuration from .env file."""

import os
from pathlib import Path
from typing import Optional


def load_env_file(env_path: Optional[str] = None):
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file. If None, looks for .env in current directory.
    """
    if env_path is None:
        # Try to find .env in current directory or parent directories
        current = Path.cwd()
        for _ in range(5):  # Search up to 5 levels
            env_file = current / ".env"
            if env_file.exists():
                env_path = env_file
                break
            current = current.parent
    
    if env_path is None:
        return  # No .env file found
    
    env_path = Path(env_path)
    if not env_path.exists():
        return
    
    # Read and parse .env file
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Set environment variable (don't override existing ones)
                if key and not os.getenv(key):
                    os.environ[key] = value


# Auto-load .env when this module is imported
load_env_file()