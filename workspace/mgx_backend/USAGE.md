# MGX Backend Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Core Concepts](#core-concepts)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Install Dependencies

```bash
cd mgx_backend
pip install -r requirements.txt
```

### Set API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

### Simplest Usage

```python
from mgx_backend.software_company import generate_repo

# Generate a project
project_path = generate_repo("Create a 2048 game")
print(f"Project created at: {project_path}")
```

### With Custom Settings

```python
from mgx_backend.software_company import generate_repo

project_path = generate_repo(
    idea="Create a todo list web app",
    investment=5.0,      # $5 budget
    n_round=5,           # Max 5 rounds
    project_name="my_todo_app",
    api_key="your-key"   # Optional if env var is set
)
```

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional
export OPENAI_MODEL="gpt-4-turbo"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export MGX_WORKSPACE="./workspace"
```

### Configuration File

Create `config.yaml`:

```yaml
llm:
  api_type: "openai"
  model: "gpt-4-turbo"
  base_url: "https://api.openai.com/v1"
  api_key: "YOUR_API_KEY"
  temperature: 0.7

project:
  workspace: "./workspace"
```

Load configuration:

```python
from mgx_backend.config import Config

config = Config.from_yaml("config.yaml")
```

### Programmatic Configuration

```python
from mgx_backend.config import Config

config = Config(
    llm={
        "api_key": "your-key",
        "model": "gpt-4-turbo",
        "temperature": 0.7
    },
    project={
        "workspace": "./my_projects"
    }
)
```

## Core Concepts

### 1. Roles

Roles are AI agents that perform specific tasks:

- **ProductManager**: Writes Product Requirements Document (PRD)
- **Architect**: Designs system architecture
- **Engineer**: Writes code

### 2. Actions

Actions are tasks that roles perform:

- **WritePRD**: Create product requirements
- **WriteDesign**: Design system architecture
- **WriteCode**: Implement the code

### 3. Messages

Messages are passed between roles:

```python
from mgx_backend.message import Message

message = Message(
    content="Create a calculator",
    role="User",
    cause_by="UserRequirement"
)
```

### 4. Environment

Environment is the message bus for role communication:

```python
from mgx_backend.environment import Environment
from mgx_backend.context import Context

ctx = Context()
env = Environment(context=ctx)
```

### 5. Team

Team manages multiple roles:

```python
from mgx_backend.team import Team
from mgx_backend.roles import ProductManager, Architect, Engineer

team = Team()
team.hire([ProductManager(), Architect(), Engineer()])
team.invest(5.0)
await team.run(n_round=5, idea="Create a game")
```

## API Reference

### generate_repo()

Main entry point for project generation.

```python
def generate_repo(
    idea: str,              # User requirement
    investment: float = 3.0, # Budget in dollars
    n_round: int = 5,       # Max rounds
    project_name: str = "", # Optional name
    project_path: str = "", # Optional path
    api_key: str = "",      # Optional API key
) -> str:
    """Generate a complete software project."""
```

**Example:**

```python
project_path = generate_repo(
    idea="Create a weather app",
    investment=10.0,
    n_round=5
)
```

### ProjectRepo

Manage project files.

```python
from mgx_backend.project_repo import ProjectRepo

repo = ProjectRepo("/path/to/project")

# Access documentation
prd = await repo.docs.prd.read("prd.md")
design = await repo.docs.system_design.read("system_design.md")

# Access source code
src_files = repo.srcs.all_files

# Save files
await repo.save_prd("# PRD Content")
await repo.save_design("# Design Content")
```

### Config

Configuration management.

```python
from mgx_backend.config import Config

# Default config
config = Config.default()

# From YAML
config = Config.from_yaml("config.yaml")

# Update project settings
config.update_project(
    project_name="my_app",
    project_path="./projects/my_app"
)
```

### Context

Global context for the system.

```python
from mgx_backend.context import Context

ctx = Context(config=config)

# Get LLM instance
llm = ctx.llm()

# Access cost manager
cost_manager = ctx.cost_manager

# Get/set project path
project_path = ctx.project_path
ctx.project_path = "/new/path"
```

### Team

Manage team of roles.

```python
from mgx_backend.team import Team

team = Team(context=ctx)

# Hire roles
team.hire([ProductManager(), Architect(), Engineer()])

# Set budget
team.invest(10.0)

# Run project
await team.run(n_round=5, idea="Create an app")
```

## Examples

### Example 1: Basic Project Generation

```python
from mgx_backend.software_company import generate_repo

project_path = generate_repo("Create a calculator app")
print(f"Project: {project_path}")
```

### Example 2: Custom Configuration

```python
from mgx_backend.config import Config
from mgx_backend.context import Context
from mgx_backend.team import Team
from mgx_backend.roles import ProductManager, Architect, Engineer

async def create_project():
    config = Config(
        llm={"api_key": "your-key", "model": "gpt-4-turbo"},
        project={"workspace": "./projects"}
    )
    
    ctx = Context(config=config)
    team = Team(context=ctx)
    team.hire([ProductManager(), Architect(), Engineer()])
    team.invest(5.0)
    
    await team.run(n_round=5, idea="Create a timer app")
    return ctx.project_path

import asyncio
project_path = asyncio.run(create_project())
```

### Example 3: Access Generated Files

```python
from mgx_backend.project_repo import ProjectRepo
import asyncio

async def read_files(project_path):
    repo = ProjectRepo(project_path)
    
    # Read PRD
    prd = await repo.docs.prd.read("prd.md")
    print("PRD:", prd[:200])
    
    # Read design
    design = await repo.docs.system_design.read("system_design.md")
    print("Design:", design[:200])
    
    # List source files
    print("Source files:", repo.srcs.all_files)

asyncio.run(read_files("/path/to/project"))
```

### Example 4: Cost Tracking

```python
from mgx_backend.context import Context

ctx = Context()
ctx.cost_manager.max_budget = 5.0

# After running
print(ctx.cost_manager.get_summary())
```

### Example 5: Custom Role

```python
from mgx_backend.role import Role
from mgx_backend.action import Action

class CustomAction(Action):
    name = "CustomAction"
    
    async def run(self, context: str) -> str:
        prompt = f"Process: {context}"
        return await self.llm.ask(prompt)

class CustomRole(Role):
    name = "CustomRole"
    profile = "Custom Role"
    goal = "Do custom tasks"
    
    def __init__(self):
        super().__init__()
        self.set_actions([CustomAction])
        self.watch({"SomeAction"})

# Use custom role
team.hire([CustomRole()])
```

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution:**

```bash
export OPENAI_API_KEY="your-key"
```

Or pass directly:

```python
generate_repo(idea="...", api_key="your-key")
```

### Issue: "Budget exceeded"

**Solution:** Increase investment:

```python
generate_repo(idea="...", investment=10.0)
```

### Issue: "No module named 'mgx_backend'"

**Solution:**

```bash
cd /workspace
pip install -e mgx_backend/
```

Or add to PYTHONPATH:

```bash
export PYTHONPATH="/workspace:$PYTHONPATH"
```

### Issue: Project generation takes too long

**Solution:** Reduce rounds or use faster model:

```python
generate_repo(
    idea="...",
    n_round=3,  # Reduce rounds
)

# Or use faster model
config.llm.model = "gpt-3.5-turbo"
```

### Issue: Generated code is incomplete

**Solution:** Increase budget and rounds:

```python
generate_repo(
    idea="...",
    investment=10.0,
    n_round=8
)
```

## Best Practices

1. **Start Small**: Begin with simple projects to understand the workflow
2. **Set Appropriate Budget**: Complex projects need higher investment
3. **Clear Requirements**: Provide detailed, specific requirements
4. **Monitor Costs**: Check cost_manager regularly
5. **Save Outputs**: Always save generated files to ProjectRepo
6. **Iterate**: Use multiple rounds for complex projects

## Support

For issues and questions:
- Check the README.md
- Review examples in `examples/` directory
- Check the architecture analysis in `/workspace/docs/metagpt_architecture_analysis.md`