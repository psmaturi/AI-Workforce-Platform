from langchain_ollama import ChatOllama
from app.config import settings

def get_ollama_llm(model: str = None, temperature: float = 0.0) -> ChatOllama:
    """Instantiate ChatOllama LLM client.
    """
    model_name = model or settings.OLLAMA_MODEL
    return ChatOllama(
        model=model_name,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=temperature
    )
