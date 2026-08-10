"""Quick diagnostic to test the full RAG flow from the server's context."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import asyncio
from app.agent.state import AgentState
from app.agent.nodes import response_generation_node

async def test():
    state = AgentState(
        question="What is the learning budget policy?",
        intent="Company Policy",
        tool_selected="CompanyPolicyTool",
        tool_result={"policy_topic": "learning budget"},
        messages=[],
        final_response="",
        metadata={},
    )
    print("Running response_generation_node with Company Policy intent...")
    result = await response_generation_node(state)
    print("\n=== Final Response ===")
    print(result["final_response"][:500])

asyncio.run(test())
