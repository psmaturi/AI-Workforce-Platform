"""Singleton ChromaDB Vector Store Module."""

import threading
import os
from typing import Optional
from app.config import settings
from app.rag.embeddings import get_embeddings
from app.utils.logger import logger


class VectorStoreManager:
    """Thread-safe singleton manager for the ChromaDB vector store."""

    _instance = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_store(cls):
        """Return the singleton Chroma vector store instance.

        Creates the persist directory if it does not exist.
        Loads existing vectors from disk on restart.

        Returns:
            Chroma: Singleton ChromaDB vector store instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.info(
                        f"Initializing ChromaDB vector store at "
                        f"'{settings.CHROMA_PERSIST_DIR}' "
                        f"(collection: '{settings.CHROMA_COLLECTION_NAME}')..."
                    )
                    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
                    embeddings = get_embeddings()

                    try:
                        from langchain_chroma import Chroma
                    except ImportError:
                        from langchain_community.vectorstores import Chroma

                    cls._instance = Chroma(
                        collection_name=settings.CHROMA_COLLECTION_NAME,
                        embedding_function=embeddings,
                        persist_directory=settings.CHROMA_PERSIST_DIR,
                    )
                    count = cls._instance._collection.count()
                    logger.info(
                        f"ChromaDB ready. Documents in collection: {count}"
                    )
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing purposes)."""
        with cls._lock:
            cls._instance = None


def get_vector_store():
    """Helper to access the singleton ChromaDB vector store.

    Returns:
        Chroma: Singleton ChromaDB instance.
    """
    return VectorStoreManager.get_store()
