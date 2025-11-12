"""Simple test to verify MGX Backend works."""

import os
import asyncio
from mgx_backend.config import Config
from mgx_backend.context import Context
from mgx_backend.llm import OpenAILLM
from mgx_backend.cost_manager import CostManager


async def test_llm():
    """Test LLM connection."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    print("🧪 Testing LLM connection...")
    
    llm = OpenAILLM(
        api_key=api_key,
        model="gpt-4-turbo"
    )
    llm.cost_manager = CostManager()
    
    try:
        response = await llm.ask("Say 'Hello, MGX Backend!'")
        print(f"✅ LLM Response: {response}")
        print(f"💰 Cost: ${llm.cost_manager.total_cost:.4f}")
        return True
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


async def test_simple_workflow():
    """Test a simple workflow."""
    from mgx_backend.team import Team
    from mgx_backend.roles import ProductManager
    
    print("\n🧪 Testing simple workflow...")
    
    config = Config.default()
    ctx = Context(config=config)
    
    team = Team(context=ctx)
    team.hire([ProductManager()])
    team.invest(2.0)
    
    try:
        await team.run(
            n_round=1,
            idea="Create a simple hello world program"
        )
        print("✅ Workflow test passed")
        return True
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 MGX Backend Test Suite\n")
    
    # Test 1: LLM connection
    llm_ok = await test_llm()
    
    if llm_ok:
        # Test 2: Simple workflow
        workflow_ok = await test_simple_workflow()
        
        if workflow_ok:
            print("\n✅ All tests passed!")
        else:
            print("\n⚠️ Some tests failed")
    else:
        print("\n❌ Cannot proceed without valid API key")


if __name__ == "__main__":
    asyncio.run(main())