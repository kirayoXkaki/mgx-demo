#!/usr/bin/env python
"""Command-line interface for MGX Backend."""

import sys
import argparse
from mgx_backend.software_company import generate_repo


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MGX Backend - AI-powered software development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a simple project
  python cli.py "Create a calculator app"
  
  # With custom settings
  python cli.py "Create a todo app" --investment 5.0 --rounds 5
  
  # Specify project name
  python cli.py "Create a game" --name my_game --investment 10.0
        """
    )
    
    parser.add_argument(
        "idea",
        help="Your project idea (e.g., 'Create a 2048 game')"
    )
    
    parser.add_argument(
        "--investment",
        type=float,
        default=3.0,
        help="Budget in dollars (default: 3.0)"
    )
    
    parser.add_argument(
        "--rounds",
        type=int,
        default=5,
        help="Maximum collaboration rounds (default: 5)"
    )
    
    parser.add_argument(
        "--name",
        default="",
        help="Project name (default: auto-generated)"
    )
    
    parser.add_argument(
        "--path",
        default="",
        help="Custom project path (default: ./workspace/<name>)"
    )
    
    parser.add_argument(
        "--api-key",
        default="",
        help="OpenAI API key (default: from OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 MGX Backend - Generating project...")
        print(f"💡 Idea: {args.idea}")
        print(f"💰 Budget: ${args.investment}")
        print(f"🔄 Max rounds: {args.rounds}\n")
        
        project_path = generate_repo(
            idea=args.idea,
            investment=args.investment,
            n_round=args.rounds,
            project_name=args.name,
            project_path=args.path,
            api_key=args.api_key
        )
        
        print(f"\n✨ Success! Project generated at:")
        print(f"   {project_path}")
        print(f"\n📂 Next steps:")
        print(f"   cd {project_path}")
        print(f"   # Review the generated files")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()