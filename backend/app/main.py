"""FastAPI Main Application Entrypoint Module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.logger import logger
from app.llm.ollama_client import OllamaClientManager
from app.agent.workforce_agent import get_workforce_agent
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import get_vector_store
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.ml import router as ml_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    # Phase 1: LLM
    logger.info("Initializing ChatOllama...")
    try:
        OllamaClientManager.get_client()
    except Exception as e:
        logger.warning(f"Could not connect to Ollama daemon on startup: {e}")

    # Phase 2: LangGraph Agent
    logger.info("Initializing WorkforceAgent...")
    # Triggers build_workforce_graph() → logs "Compiling LangGraph..." and "LangGraph compiled successfully."
    get_workforce_agent()

    # Phase 3: RAG — Embedding Model + ChromaDB
    logger.info("Initializing Embedding Model...")
    try:
        get_embeddings()
    except Exception as e:
        logger.warning(f"Embedding model initialization warning: {e}")

    logger.info("Initializing ChromaDB Vector Store...")
    try:
        get_vector_store()
    except Exception as e:
        logger.warning(f"ChromaDB initialization warning: {e}")

    logger.info("Application Ready.")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade AI Workforce Intelligence Platform Backend API",
    lifespan=lifespan,
)

# CORS — allow React dev server and production frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Alternative dev port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(ml_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
