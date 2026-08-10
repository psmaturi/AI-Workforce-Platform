"""Memory Saver Module for Stateful Graph Checkpointing."""

import threading
from typing import Optional
from langgraph.checkpoint.memory import MemorySaver
from app.utils.logger import logger

class MemoryManager:
    """Singleton MemorySaver Checkpointer Manager."""
    
    _checkpointer: Optional[MemorySaver] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_checkpointer(cls) -> MemorySaver:
        """Get or initialize the singleton MemorySaver checkpointer instance.
        
        Returns:
            MemorySaver: Stateful memory checkpointer instance.
        """
        if cls._checkpointer is None:
            with cls._lock:
                if cls._checkpointer is None:
                    cls._checkpointer = MemorySaver()
        return cls._checkpointer

def get_memory_saver() -> MemorySaver:
    """Helper function returning the global MemorySaver instance.
    
    Returns:
        MemorySaver: Global memory checkpointer.
    """
    return MemoryManager.get_checkpointer()
