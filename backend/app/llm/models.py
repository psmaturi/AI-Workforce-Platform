from pydantic import BaseModel
from typing import List, Optional

class ModelInfo(BaseModel):
    name: str
    provider: str
    description: str
    context_window: int
    is_active: bool = True

SUPPORTED_MODELS: List[ModelInfo] = [
    ModelInfo(
        name="qwen2.5:7b",
        provider="Ollama",
        description="Qwen 2.5 7B model tuned for reasoning, code, and industrial instruction following.",
        context_window=32768
    ),
    ModelInfo(
        name="llama3.1:8b",
        provider="Ollama",
        description="Llama 3.1 8B open model.",
        context_window=128000
    )
]

def list_supported_models() -> List[ModelInfo]:
    return SUPPORTED_MODELS
