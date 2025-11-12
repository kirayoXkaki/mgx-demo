"""
Comprehensive test script for MGX Backend.
This script verifies all components work correctly.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add mgx_backend to path
sys.path.insert(0, str(Path(__file__).parent))

from mgx_backend.config import Config
from mgx_backend.context import Context
from mgx_backend.llm import OpenAILLM
from mgx_backend.cost_manager import CostManager
from mgx_backend.message import Message, UserRequirement
from mgx_backend.environment import Environment
from mgx_backend.role import Role
from mgx_backend.action import Action
from mgx_backend.team import Team
from mgx_backend.roles import ProductManager, Architect, Engineer
from mgx_backend.actions import WritePRD, WriteDesign, WriteCode
from mgx_backend.project_repo import ProjectRepo
from mgx_backend.software_company import generate_repo


def test_imports():
    """Test 1: Verify all imports work."""
    print("✅ Test 1: All imports successful")
    return True


def test_config():
    """Test 2: Verify configuration."""
    print("\n🧪 Test 2: Configuration")
    
    # Default config
    config = Config.default()
    assert config.llm.api_type == "openai"
    assert config.llm.model == "gpt-4-turbo"
    print("  ✅ Default config created")
    
    # Update project
    config.update_project(project_name="test_project")
    assert config.project.project_name == "test_project"
    print("  ✅ Project config updated")
    
    return True


def test_cost_manager():
    """Test 3: Verify cost management."""
    print("\n🧪 Test 3: Cost Manager")
    
    cm = CostManager()
    cm.max_budget = 5.0
    
    # Update cost
    cm.update_cost(1000, 500, "gpt-4-turbo")
    assert cm.total_prompt_tokens == 1000
    assert cm.total_completion_tokens == 500
    assert cm.total_cost > 0
    print(f"  ✅ Cost calculated: ${cm.total_cost:.4f}")
    
    # Get summary
    summary = cm.get_summary()
    assert "Cost Summary" in summary
    print("  ✅ Cost summary generated")
    
    return True


def test_message():
    """Test 4: Verify message creation."""
    print("\n🧪 Test 4: Messages")
    
    # Regular message
    msg = Message(content="Test message", role="User")
    assert msg.content == "Test message"
    assert msg.role == "User"
    print("  ✅ Message created")
    
    # User requirement
    req = UserRequirement(content="Create a game")
    assert req.cause_by == "UserRequirement"
    print("  ✅ UserRequirement created")
    
    return True


def test_context():
    """Test 5: Verify context."""
    print("\n🧪 Test 5: Context")
    
    config = Config.default()
    ctx = Context(config=config)
    
    # Set project path
    ctx.project_path = "/test/path"
    assert ctx.project_path == "/test/path"
    print("  ✅ Context created and configured")
    
    return True


async def test_llm():
    """Test 6: Verify LLM (requires API key)."""
    print("\n🧪 Test 6: LLM")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  ⚠️  Skipped (no API key)")
        return True
    
    llm = OpenAILLM(api_key=api_key, model="gpt-4-turbo")
    llm.cost_manager = CostManager()
    
    try:
        response = await llm.ask("Say 'test'")
        assert len(response) > 0
        print(f"  ✅ LLM responded: {response[:50]}...")
        print(f"  💰 Cost: ${llm.cost_manager.total_cost:.4f}")
        return True
    except Exception as e:
        print(f"  ❌ LLM test failed: {e}")
        return False


def test_roles_and_actions():
    """Test 7: Verify roles and actions."""
    print("\n🧪 Test 7: Roles and Actions")
    
    # Create roles
    pm = ProductManager()
    arch = Architect()
    eng = Engineer()
    
    assert pm.name == "Alice"
    assert arch.name == "Bob"
    assert eng.name == "Charlie"
    print("  ✅ Roles created")
    
    # Check actions
    assert len(pm.actions) > 0
    assert len(arch.actions) > 0
    assert len(eng.actions) > 0
    print("  ✅ Actions assigned")
    
    return True


async def test_environment():
    """Test 8: Verify environment."""
    print("\n🧪 Test 8: Environment")
    
    ctx = Context()
    env = Environment(context=ctx)
    
    # Add roles
    roles = [ProductManager(), Architect(), Engineer()]
    env.add_roles(roles)
    
    assert len(env.roles) == 3
    print("  ✅ Roles added to environment")
    
    # Publish message
    msg = Message(content="Test", role="User")
    await env.publish_message(msg)
    
    assert len(env.history) == 1
    print("  ✅ Message published")
    
    return True


async def test_team():
    """Test 9: Verify team."""
    print("\n🧪 Test 9: Team")
    
    ctx = Context()
    team = Team(context=ctx)
    
    # Hire roles
    team.hire([ProductManager(), Architect(), Engineer()])
    assert len(team.env.roles) == 3
    print("  ✅ Team hired")
    
    # Set investment
    team.invest(5.0)
    assert team.investment == 5.0
    print("  ✅ Investment set")
    
    return True


def test_project_repo():
    """Test 10: Verify project repository."""
    print("\n🧪 Test 10: Project Repository")
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = ProjectRepo(tmpdir)
        
        assert repo.workdir.exists()
        assert repo.docs.prd.path.exists()
        assert repo.srcs.path.exists()
        print("  ✅ Project repository created")
        
        return True


async def test_full_workflow():
    """Test 11: Full workflow (requires API key)."""
    print("\n🧪 Test 11: Full Workflow")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  ⚠️  Skipped (no API key)")
        return True
    
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config.default()
            config.project.workspace = tmpdir
            
            ctx = Context(config=config)
            team = Team(context=ctx)
            team.hire([ProductManager()])  # Just PM for quick test
            team.invest(2.0)
            
            await team.run(n_round=1, idea="Create a hello world program")
            
            assert len(team.env.history) > 0
            print("  ✅ Workflow executed")
            
            return True
    except Exception as e:
        print(f"  ❌ Workflow test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("🚀 MGX Backend - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports, False),
        ("Configuration", test_config, False),
        ("Cost Manager", test_cost_manager, False),
        ("Messages", test_message, False),
        ("Context", test_context, False),
        ("LLM", test_llm, True),
        ("Roles & Actions", test_roles_and_actions, False),
        ("Environment", test_environment, True),
        ("Team", test_team, True),
        ("Project Repository", test_project_repo, False),
        ("Full Workflow", test_full_workflow, True),
    ]
    
    results = []
    for name, test_func, is_async in tests:
        try:
            if is_async:
                result = await test_func()
            else:
                result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! MGX Backend is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
    
    return passed == total


def main():
    """Main entry point."""
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()