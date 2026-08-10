"""LangGraph StateGraph Workflow Compilation Module."""

import threading
from typing import Optional, Any
from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes import intent_detection_node, tool_execution_node, response_generation_node
from app.agent.memory import get_memory_saver
from app.utils.logger import logger

def build_workforce_graph():
    """Build and compile the Agentic AI Workforce Intelligence StateGraph.
    
    Returns:
        CompiledStateGraph: Compiled state graph with memory checkpointer.
    """
    logger.info("Compiling LangGraph...")
    
    # 1. Instantiate StateGraph with AgentState
    workflow = StateGraph(AgentState)
    
    # 2. Add Workflow Nodes
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("tool_execution", tool_execution_node)
    workflow.add_node("response_generation", response_generation_node)
    
    # 3. Add Workflow Edges (Sequential Agentic Pipeline)
    workflow.add_edge(START, "intent_detection")
    workflow.add_edge("intent_detection", "tool_execution")
    workflow.add_edge("tool_execution", "response_generation")
    workflow.add_edge("response_generation", END)
    
    # 4. Compile with Memory Checkpointer
    checkpointer = get_memory_saver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    logger.info("LangGraph compiled successfully.")
    
    return compiled_graph

_compiled_app: Optional[Any] = None
_graph_lock: threading.Lock = threading.Lock()

def get_workforce_app():
    """Returns singleton instance of the compiled LangGraph application.
    
    Returns:
        CompiledStateGraph: Compiled LangGraph application.
    """
    global _compiled_app
    if _compiled_app is None:
        with _graph_lock:
            if _compiled_app is None:
                _compiled_app = build_workforce_graph()
    return _compiled_app
