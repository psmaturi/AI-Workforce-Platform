"""Text Splitter Module — Configurable Recursive Character Splitter."""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings
from app.utils.logger import logger


def get_text_splitter(
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> RecursiveCharacterTextSplitter:
    """Return a configured RecursiveCharacterTextSplitter.

    Args:
        chunk_size (int, optional): Override chunk size. Defaults to settings.CHUNK_SIZE.
        chunk_overlap (int, optional): Override chunk overlap. Defaults to settings.CHUNK_OVERLAP.

    Returns:
        RecursiveCharacterTextSplitter: Configured splitter instance.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )


def split_documents(documents: List[Document]) -> List[Document]:
    """Split a list of documents into chunks using the configured splitter.

    Preserves all source metadata in every chunk.

    Args:
        documents (List[Document]): Raw loaded documents.

    Returns:
        List[Document]: Chunked documents ready for embedding.
    """
    if not documents:
        logger.warning("No documents provided to split.")
        return []

    splitter = get_text_splitter()
    chunks = splitter.split_documents(documents)
    logger.info(
        f"Text splitting complete. "
        f"Input documents: {len(documents)} | "
        f"Output chunks: {len(chunks)} | "
        f"Chunk size: {settings.CHUNK_SIZE} | "
        f"Chunk overlap: {settings.CHUNK_OVERLAP}"
    )
    return chunks
