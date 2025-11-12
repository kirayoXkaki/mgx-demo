"""Advanced usage example for MGX Backend."""

import asyncio
import os
from mgx_backend.config import Config
from mgx_backend.context import Context
from mgx_backend.team import Team
from mgx_backend.roles import ProductManager, Architect, Engineer
from mgx_backend.project_repo import ProjectRepo


async def create_custom_project():
    """Create a project with custom configuration."""
    
    # Create custom configuration
    config = Config(
        llm={
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4-turbo",
            "temperature": 0.7,
        },
        project={
            "workspace": "./my_projects",
            "project_name": "my_calculator_app"
        }
    )
    
    # Create context
    ctx = Context(config=config)
    
    # Create team
    team = Team(context=ctx)
    
    # Hire specific roles
    team.hire([
        ProductManager(),
        Architect(),
        Engineer()
    ])
    
    # Set budget
    team.invest(10.0)  # $10 budget
    
    # Run project
    print("🚀 Starting custom project...")
    history = await team.run(
        n_round=5,
        idea="Create a scientific calculator web application with advanced functions"
    )
    
    # Save outputs
    repo = ProjectRepo(ctx.project_path)
    
    for message in history:
        if message.cause_by == "WritePRD":
            await repo.save_prd(message.content)
        elif message.cause_by == "WriteDesign":
            await repo.save_design(message.content)
        elif message.cause_by == "WriteCode":
            await repo.save_code_files(message.content)
    
    print(f"\n✅ Project created at: {ctx.project_path}")
    print(f"\n{repo}")
    
    return ctx.project_path


async def create_multiple_projects():
    """Create multiple projects in parallel."""
    
    ideas = [
        "Create a weather app",
        "Create a note-taking app",
        "Create a timer app"
    ]
    
    tasks = []
    for idea in ideas:
        config = Config.default()
        ctx = Context(config=config)
        team = Team(context=ctx)
        team.hire([ProductManager(), Architect(), Engineer()])
        team.invest(3.0)
        
        tasks.append(team.run(n_round=3, idea=idea))
    
    # Run all projects in parallel
    results = await asyncio.gather(*tasks)
    
    print(f"\n✅ Created {len(results)} projects")


def main():
    # Run custom project
    project_path = asyncio.run(create_custom_project())
    print(f"\nProject path: {project_path}")
    
    # Uncomment to create multiple projects
    # asyncio.run(create_multiple_projects())


if __name__ == "__main__":
    main()