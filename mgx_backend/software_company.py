"""Main entry point for MGX Backend - software company simulation."""

import asyncio
from pathlib import Path

from mgx_backend.config import Config
from mgx_backend.context import Context
from mgx_backend.team import Team
from mgx_backend.roles import ProductManager, Architect, Engineer
from mgx_backend.project_repo import ProjectRepo


def generate_repo(
    idea: str,
    investment: float = 3.0,
    n_round: int = 5,
    project_name: str = "",
    project_path: str = "",
    api_key: str = "",
) -> str:
    """
    Generate a complete software project from an idea.
    
    Args:
        idea: User requirement description
        investment: Budget in dollars (default: 3.0)
        n_round: Maximum collaboration rounds (default: 5)
        project_name: Optional project name
        project_path: Optional custom project path
        api_key: OpenAI API key (optional, can use env var)
    
    Returns:
        str: Path to the generated project
    
    Example:
        >>> project_path = generate_repo("Create a 2048 game")
        >>> print(f"Project created at: {project_path}")
    """
    # Create configuration
    config = Config.default()
    
    if api_key:
        config.llm.api_key = api_key
    
    if not config.llm.api_key:
        raise ValueError(
            "OpenAI API key not found. "
            "Please set OPENAI_API_KEY environment variable or pass api_key parameter."
        )
    
    # Update project configuration
    config.update_project(
        project_path=project_path,
        project_name=project_name or _generate_project_name(idea)
    )
    
    # Create context
    ctx = Context(config=config)
    
    # Create team
    company = Team(context=ctx)
    
    # Hire roles
    company.hire([
        ProductManager(),
        Architect(),
        Engineer(),
    ])
    
    # Set investment
    company.invest(investment)
    
    # Run the team
    asyncio.run(_run_and_save(company, idea, n_round, ctx))
    
    return ctx.project_path


async def _run_and_save(company: Team, idea: str, n_round: int, ctx: Context):
    """Run the team and save outputs."""
    # Run team collaboration
    history = await company.run(n_round=n_round, idea=idea)
    
    # Create project repository
    repo = ProjectRepo(ctx.project_path)
    
    # Save outputs from history
    for message in history:
        if message.cause_by == "WritePRD":
            await repo.save_prd(message.content)
            print(f"✅ Saved PRD to {repo.docs.prd.path}")
            
        elif message.cause_by == "WriteDesign":
            await repo.save_design(message.content)
            print(f"✅ Saved Design to {repo.docs.system_design.path}")
            
        elif message.cause_by == "WriteCode":
            await repo.save_code_files(message.content)
            print(f"✅ Saved Code to {repo.srcs.path}")
    
    print(f"\n📁 Project repository: {repo.workdir}")
    print(f"\n{repo}")


def _generate_project_name(idea: str) -> str:
    """Generate a project name from the idea."""
    # Simple implementation: take first few words and make them lowercase
    words = idea.lower().split()[:3]
    name = "_".join(w for w in words if w.isalnum())
    
    if not name:
        import time
        name = f"project_{int(time.time())}"
    
    return name


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python software_company.py '<your idea>'")
        print("Example: python software_company.py 'Create a 2048 game'")
        sys.exit(1)
    
    idea = sys.argv[1]
    project_path = generate_repo(idea)
    print(f"\n✨ Project generated successfully at: {project_path}")