"""Singleton Embedding Model Module using Sentence Transformers."""

import threading
from typing import Optional
from app.config import settings
from app.utils.logger import logger


class EmbeddingManager:
    """Thread-safe singleton manager for the HuggingFace embedding model."""

    _instance = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_embeddings(cls):
        """Return the singleton HuggingFaceEmbeddings instance.

        Initializes the embedding model on first call and caches it.

        Returns:
            HuggingFaceEmbeddings: Singleton embedding model instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.info(
                        f"Initializing embedding model '{settings.EMBEDDING_MODEL}'..."
                    )
                    try:
                        from langchain_huggingface import HuggingFaceEmbeddings

                        cls._instance = HuggingFaceEmbeddings(
                            model_name=settings.EMBEDDING_MODEL,
                            model_kwargs={"device": "cpu"},
                            encode_kwargs={"normalize_embeddings": True},
                        )
                    except ImportError:
                        # Fallback to langchain_community
                        from langchain_community.embeddings import HuggingFaceEmbeddings

                        cls._instance = HuggingFaceEmbeddings(
                            model_name=settings.EMBEDDING_MODEL,
                            model_kwargs={"device": "cpu"},
                            encode_kwargs={"normalize_embeddings": True},
                        )
                    logger.info("Embedding model initialized successfully.")
        return cls._instance


def get_embeddings():
    """Helper to access the singleton embedding model instance.

    Returns:
        HuggingFaceEmbeddings: Initialized embedding model.
    """
    return EmbeddingManager.get_embeddings()
