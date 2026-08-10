from langchain_ollama import OllamaEmbeddings
from app.config import settings

def get_ollama_embeddings(model: str = None) -> OllamaEmbeddings:
    """Instantiate OllamaEmbeddings client.
    """
    model_name = model or settings.OLLAMA_MODEL
    return OllamaEmbeddings(
        model=model_name,
        base_url=settings.OLLAMA_BASE_URL
    )
