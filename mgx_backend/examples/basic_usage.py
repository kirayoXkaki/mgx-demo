"""Basic usage example for MGX Backend."""

import os
from mgx_backend.software_company import generate_repo
from mgx_backend.project_repo import ProjectRepo


def main():
    # Set your OpenAI API key
    # Option 1: Set environment variable
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    # Option 2: Pass directly to generate_repo
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    # Generate a project
    print("🚀 Generating project...")
    project_path = generate_repo(
        idea="Create a simple todo list web application with HTML, CSS, and JavaScript",
        investment=5.0,  # $5 budget
        n_round=5,       # Max 5 rounds
        api_key=api_key
    )
    
    print(f"\n✅ Project generated at: {project_path}")
    
    # Access the project repository
    repo = ProjectRepo(project_path)
    print(f"\n📂 Project structure:")
    print(repo)
    
    # Read generated files
    print(f"\n📄 Generated files:")
    print(f"  Docs: {repo.docs.all_files}")
    print(f"  Sources: {repo.srcs.all_files}")


if __name__ == "__main__":
    main()