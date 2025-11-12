# MGX Backend - Simplified MetaGPT Implementation

A simplified implementation of MetaGPT's multi-agent software development system.

## Features

- **Multi-Agent Collaboration**: ProductManager, Architect, and Engineer roles working together
- **OpenAI Integration**: Uses OpenAI API for LLM capabilities
- **Project Repository Management**: Organized file structure for generated projects
- **Cost Management**: Track and limit API usage costs
- **Async Workflow**: Efficient asynchronous execution

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from mgx_backend.software_company import generate_repo
from mgx_backend.project_repo import ProjectRepo

# Set your OpenAI API key
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Generate a project
project_path = generate_repo("Create a 2048 game")
print(f"Project created at: {project_path}")

# Access the project repository
repo = ProjectRepo(project_path)
print(repo)
```

## Architecture

```
User Requirement
    ↓
generate_repo()
    ↓
Team (manages roles)
    ↓
Environment (message bus)
    ↓
Roles (ProductManager, Architect, Engineer)
    ↓
Actions (WritePRD, WriteDesign, WriteCode)
    ↓
LLM (OpenAI)
    ↓
ProjectRepo (organized output)
```

## Configuration

Create a `config.yaml` file:

```yaml
llm:
  api_type: "openai"
  model: "gpt-4-turbo"
  base_url: "https://api.openai.com/v1"
  api_key: "YOUR_API_KEY"

project:
  workspace: "./workspace"
```

Or set environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4-turbo"
```

## Project Structure

```
mgx_backend/
├── __init__.py
├── config.py           # Configuration management
├── context.py          # Global context and LLM management
├── llm.py             # LLM wrapper for OpenAI
├── cost_manager.py    # Cost tracking
├── message.py         # Message schema
├── environment.py     # Message bus for role communication
├── role.py            # Base role class
├── action.py          # Base action class
├── team.py            # Team management
├── roles/
│   ├── __init__.py
│   ├── product_manager.py
│   ├── architect.py
│   └── engineer.py
├── actions/
│   ├── __init__.py
│   ├── write_prd.py
│   ├── write_design.py
│   └── write_code.py
├── project_repo.py    # Project repository management
└── software_company.py # Main entry point
```

## Usage Examples

### Basic Usage

```python
import asyncio
from mgx_backend.software_company import generate_repo

# Simple project generation
project_path = generate_repo(
    idea="Create a todo list web app",
    investment=5.0,  # Max $5 budget
    n_round=5        # Max 5 rounds of collaboration
)
```

### Advanced Usage

```python
from mgx_backend.config import Config
from mgx_backend.context import Context
from mgx_backend.team import Team
from mgx_backend.roles import ProductManager, Architect, Engineer

async def create_custom_project():
    # Custom configuration
    config = Config(
        api_key="your-key",
        model="gpt-4-turbo",
        workspace="./my_projects"
    )
    
    # Create context
    ctx = Context(config=config)
    
    # Create team
    team = Team(context=ctx)
    
    # Hire roles
    team.hire([
        ProductManager(),
        Architect(),
        Engineer()
    ])
    
    # Set budget
    team.invest(10.0)
    
    # Run project
    await team.run(
        n_round=5,
        idea="Create a calculator app"
    )
    
    return ctx.project_path

# Run
project_path = asyncio.run(create_custom_project())
```

### Access Generated Files

```python
from mgx_backend.project_repo import ProjectRepo

repo = ProjectRepo("/path/to/project")

# Read PRD
prd = repo.docs.prd.read("prd.md")

# Read design document
design = repo.docs.system_design.read("system_design.md")

# List all source files
src_files = repo.srcs.all_files
print(f"Generated files: {src_files}")
```

## API Reference

### generate_repo()

```python
def generate_repo(
    idea: str,              # User requirement
    investment: float = 3.0, # Budget in dollars
    n_round: int = 5,       # Max collaboration rounds
    project_name: str = "", # Optional project name
    project_path: str = "", # Optional custom path
) -> str:
    """Generate a complete software project from an idea."""
```

### ProjectRepo

```python
class ProjectRepo:
    """Manage project file structure."""
    
    @property
    def docs(self) -> DocRepository:
        """Access documentation files."""
    
    @property
    def srcs(self) -> FileRepository:
        """Access source code files."""
    
    @property
    def workdir(self) -> Path:
        """Get project working directory."""
```

## Cost Management

The system automatically tracks API costs:

```python
from mgx_backend.context import Context

ctx = Context()
ctx.cost_manager.max_budget = 5.0  # Set $5 limit

# After running
print(f"Total cost: ${ctx.cost_manager.total_cost}")
print(f"Tokens used: {ctx.cost_manager.total_tokens}")
```

## Extending the System

### Add Custom Role

```python
from mgx_backend.role import Role
from mgx_backend.action import Action

class CustomAction(Action):
    async def run(self, context: str) -> str:
        prompt = f"Do something with: {context}"
        return await self.llm.ask(prompt)

class CustomRole(Role):
    name = "CustomRole"
    profile = "Custom Role"
    goal = "Do custom tasks"
    
    def __init__(self):
        super().__init__()
        self.set_actions([CustomAction])
```

### Add Custom Action

```python
from mgx_backend.action import Action

class CustomAction(Action):
    async def run(self, context: str) -> str:
        # Your custom logic
        prompt = self.build_prompt(context)
        response = await self.llm.ask(prompt)
        return response
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.