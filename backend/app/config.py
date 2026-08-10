"""Application Settings and Environment Configuration Module."""

import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        """Application settings loaded from environment variables / .env file."""

        # --- General ---
        PROJECT_NAME: str = "AI Workforce Intelligence Platform"
        VERSION: str = "1.0.0"
        ENVIRONMENT: str = "development"

        # --- Ollama LLM ---
        OLLAMA_BASE_URL: str = "http://localhost:11434"
        OLLAMA_MODEL: str = "qwen2.5:7b"
        OLLAMA_TEMPERATURE: float = 0.0

        # --- RAG: Embedding ---
        EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

        # --- RAG: Text Splitting ---
        CHUNK_SIZE: int = 700
        CHUNK_OVERLAP: int = 100

        # --- RAG: Retriever ---
        TOP_K: int = 3
        
        # --- LangGraph ---
        MAX_HISTORY_MESSAGES: int = 6

        # --- RAG: ChromaDB ---
        CHROMA_PERSIST_DIR: str = "./chroma_db"
        CHROMA_COLLECTION_NAME: str = "workforce_knowledge"

        # --- RAG: Documents ---
        DOCUMENTS_DIR: str = "./documents"

        # --- Phase 4: Database ---
        DATABASE_URL: str = "sqlite:///./workforce.db"
        DB_POOL_SIZE: int = 10
        DB_MAX_OVERFLOW: int = 20
        DB_POOL_TIMEOUT: int = 30
        DB_ECHO: bool = False

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )

except ImportError:
    from pydantic import BaseModel

    class Settings(BaseModel):
        PROJECT_NAME: str = os.getenv("PROJECT_NAME", "AI Workforce Intelligence Platform")
        VERSION: str = os.getenv("VERSION", "1.0.0")
        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

        OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.0"))

        EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "700"))
        CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
        TOP_K: int = int(os.getenv("TOP_K", "3"))
        MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "6"))
        CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "workforce_knowledge")
        DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "./documents")

        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./workforce.db")
        DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
        DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    return Settings()


settings = get_settings()
