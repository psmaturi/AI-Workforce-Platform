"""Document Loader Module — PDF, TXT, Markdown with rich metadata."""

import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from app.config import settings
from app.utils.logger import logger


def _load_pdf(file_path: Path) -> List[Document]:
    """Load a PDF file using PyPDFLoader.

    Args:
        file_path (Path): Absolute path to the PDF file.

    Returns:
        List[Document]: Loaded pages with metadata.
    """
    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader(str(file_path))
    pages = loader.load()
    for page in pages:
        page.metadata.update(
            {
                "filename": file_path.name,
                "doc_type": "pdf",
                "source": str(file_path),
            }
        )
    return pages


def _load_text(file_path: Path) -> List[Document]:
    """Load a plain text file.

    Args:
        file_path (Path): Absolute path to the TXT file.

    Returns:
        List[Document]: Single document with metadata.
    """
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return [
        Document(
            page_content=text,
            metadata={
                "filename": file_path.name,
                "doc_type": "txt",
                "source": str(file_path),
                "page": 0,
            },
        )
    ]


def _load_markdown(file_path: Path) -> List[Document]:
    """Load a Markdown file.

    Args:
        file_path (Path): Absolute path to the Markdown file.

    Returns:
        List[Document]: Single document with metadata.
    """
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return [
        Document(
            page_content=text,
            metadata={
                "filename": file_path.name,
                "doc_type": "markdown",
                "source": str(file_path),
                "page": 0,
            },
        )
    ]


LOADERS = {
    ".pdf": _load_pdf,
    ".txt": _load_text,
    ".md": _load_markdown,
    ".markdown": _load_markdown,
}


def load_documents(documents_dir: str = None) -> List[Document]:
    """Recursively scan documents directory and load all supported file types.

    Args:
        documents_dir (str, optional): Directory path. Defaults to settings.DOCUMENTS_DIR.

    Returns:
        List[Document]: All loaded documents with metadata.
    """
    target_dir = Path(documents_dir or settings.DOCUMENTS_DIR)

    if not target_dir.exists():
        logger.warning(
            f"Documents directory '{target_dir}' does not exist. "
            "Creating it — please add documents and re-run ingest.py."
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        return []

    all_documents: List[Document] = []
    loaded_files = 0
    skipped_files = 0

    for file_path in sorted(target_dir.rglob("*")):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        if suffix not in LOADERS:
            skipped_files += 1
            logger.debug(f"Skipping unsupported file type: {file_path.name}")
            continue
        try:
            docs = LOADERS[suffix](file_path)
            all_documents.extend(docs)
            loaded_files += 1
            logger.info(
                f"Loaded '{file_path.name}' — {len(docs)} page(s)."
            )
        except Exception as e:
            logger.error(f"Failed to load '{file_path.name}': {e}")
            skipped_files += 1

    logger.info(
        f"Document loading complete. "
        f"Files loaded: {loaded_files} | Skipped: {skipped_files} | "
        f"Total pages/documents: {len(all_documents)}"
    )
    return all_documents
