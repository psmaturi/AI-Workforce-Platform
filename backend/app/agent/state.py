"""State Management Module for LangGraph Workforce Agent."""

from typing import Annotated, Sequence, Dict, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """Strongly typed state container for the Workforce Intelligence Agent workflow."""
    
    messages: Annotated[Sequence[BaseMessage], add_messages]
    """Conversation message history with automatic message concatenation."""
    
    question: str
    """The current user input question."""
    
    intent: Optional[str]
    """Classified intent (e.g. Employee Career, Skill Gap, Training, Company Policy, Promotion, Greeting, General Question)."""
    
    tool_selected: Optional[str]
    """Name of the selected tool to execute."""
    
    tool_result: Optional[Dict[str, Any]]
    """Structured result returned from executing the selected tool."""
    
    final_response: Optional[str]
    """Generated final answer returned to the user."""
    
    metadata: Dict[str, Any]
    """Execution metadata including logs, intent confidence, and execution timings."""
