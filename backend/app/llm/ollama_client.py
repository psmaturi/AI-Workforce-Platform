"""Ollama LLM Client Module - Singleton Connection Manager."""

import threading
from typing import Optional
from langchain_ollama import ChatOllama
from app.config import settings
from app.utils.logger import logger

class OllamaClientManager:
    """Singleton Client Manager for ChatOllama."""
    
    _instance: Optional[ChatOllama] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_client(cls) -> ChatOllama:
        """Returns a singleton instance of ChatOllama.
        
        Guarantees that ChatOllama is initialized exactly once.
        
        Returns:
            ChatOllama: Reusable ChatOllama instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.info(
                        f"Initializing ChatOllama singleton instance with model '{settings.OLLAMA_MODEL}' "
                        f"at '{settings.OLLAMA_BASE_URL}' (num_ctx=4096, num_predict=400)..."
                    )
                    cls._instance = ChatOllama(
                        model=settings.OLLAMA_MODEL,
                        base_url=settings.OLLAMA_BASE_URL,
                        temperature=settings.OLLAMA_TEMPERATURE,
                        num_ctx=4096,
                        num_predict=400
                    )
                    logger.info("ChatOllama client initialized successfully.")
        return cls._instance

def get_llm_client() -> ChatOllama:
    """Helper function to access the single reusable ChatOllama client instance.
    
    Returns:
        ChatOllama: Singleton ChatOllama client.
    """
    return OllamaClientManager.get_client()
