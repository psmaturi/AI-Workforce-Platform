"""Retriever Module — Similarity Search against ChromaDB."""

import asyncio
from typing import List, Tuple
from langchain_core.documents import Document
from app.rag.vector_store import get_vector_store
from app.config import settings
from app.utils.logger import logger


def retrieve(query: str, k: int = None) -> List[Document]:
    """Retrieve the top-k most similar document chunks for a given query.

    This is the synchronous version. Use `aretrieve()` from async contexts
    (e.g., LangGraph async nodes) to avoid blocking the event loop.

    Args:
        query (str): User question or search query.
        k (int, optional): Number of results to return. Defaults to settings.TOP_K.

    Returns:
        List[Document]: List of relevant document chunks with metadata.
    """
    top_k = k or settings.TOP_K
    logger.info(f"Retriever invoked | Query: '{query[:80]}' | Top-K: {top_k}")

    try:
        store = get_vector_store()

        # Verify collection has documents
        doc_count = store._collection.count()
        logger.info(f"ChromaDB collection count: {doc_count}")
        if doc_count == 0:
            logger.warning(
                "ChromaDB collection is empty. "
                "Run 'python app/rag/ingest.py' to index documents."
            )
            return []

        docs = store.similarity_search(query, k=top_k)

        logger.info(f"Retrieved {len(docs)} document chunk(s).")
        for i, doc in enumerate(docs):
            src = doc.metadata.get("filename", "unknown")
            page = doc.metadata.get("page", "N/A")
            snippet = doc.page_content[:80].replace("\n", " ")
            logger.info(f"  [{i+1}] Source: {src} | Page: {page} | Snippet: {snippet}...")

        return docs

    except Exception as e:
        logger.error(f"Retrieval error: {e}", exc_info=True)
        return []


async def aretrieve(query: str, k: int = None) -> List[Document]:
    """Async-safe retrieval — runs blocking ChromaDB call in a thread executor.

    Use this from async LangGraph nodes to avoid blocking the event loop.

    Args:
        query (str): User question or search query.
        k (int, optional): Number of results to return. Defaults to settings.TOP_K.

    Returns:
        List[Document]: List of relevant document chunks with metadata.
    """
    return await asyncio.to_thread(retrieve, query, k)


def retrieve_with_scores(
    query: str, k: int = None
) -> List[Tuple[Document, float]]:
    """Retrieve top-k chunks with similarity scores (synchronous).

    Args:
        query (str): User question or search query.
        k (int, optional): Number of results. Defaults to settings.TOP_K.

    Returns:
        List[Tuple[Document, float]]: (Document, score) pairs.
    """
    top_k = k or settings.TOP_K
    try:
        store = get_vector_store()
        results = store.similarity_search_with_score(query, k=top_k)
        for doc, score in results:
            logger.info(
                f"Score: {score:.4f} | "
                f"Source: {doc.metadata.get('filename', 'unknown')}"
            )
        return results
    except Exception as e:
        logger.error(f"Retrieval with scores error: {e}", exc_info=True)
        return []


async def aretrieve_with_scores(
    query: str, k: int = None
) -> List[Tuple[Document, float]]:
    """Async-safe scored retrieval — runs in a thread executor.

    Args:
        query (str): User question or search query.
        k (int, optional): Number of results. Defaults to settings.TOP_K.

    Returns:
        List[Tuple[Document, float]]: (Document, score) pairs.
    """
    return await asyncio.to_thread(retrieve_with_scores, query, k)


def format_context(docs: List[Document]) -> str:
    """Format retrieved documents into a single context string for the LLM.

    Args:
        docs (List[Document]): Retrieved document chunks.

    Returns:
        str: Formatted context string with source citations.
    """
    if not docs:
        return "No relevant company documents found."

    sections = []
    for i, doc in enumerate(docs):
        filename = doc.metadata.get("filename", "Company Document")
        sections.append(f"SOURCE:\n{filename}\nCONTENT:\n{doc.page_content.strip()}")

    context = "\n\n".join(sections)
    logger.info(f"Context assembled. Total length: {len(context)} characters.")
    return context
