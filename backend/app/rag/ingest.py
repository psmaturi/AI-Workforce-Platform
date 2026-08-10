"""Standalone Document Ingestion Script for ChromaDB.

Run this script once (or whenever documents are added/updated):
    python app/rag/ingest.py

This will:
    1. Load all documents from the configured documents directory.
    2. Split them into chunks using RecursiveCharacterTextSplitter.
    3. Generate embeddings using sentence-transformers/all-MiniLM-L6-v2.
    4. Store and persist them in ChromaDB.
    5. Print detailed ingestion statistics.
"""

import sys
import os
import time

# Ensure root backend/ is on PYTHONPATH when running as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Force UTF-8 output on Windows to avoid cp1252 UnicodeEncodeError
sys.stdout.reconfigure(encoding="utf-8")


def run_ingestion() -> None:
    """Execute the full document ingestion pipeline."""
    from app.config import settings
    from app.utils.logger import logger
    from app.rag.document_loader import load_documents
    from app.rag.text_splitter import split_documents
    from app.rag.embeddings import get_embeddings
    from app.rag.vector_store import VectorStoreManager

    print("\n" + "=" * 60)
    print("  AI Workforce Intelligence Platform -- Document Ingestion")
    print("=" * 60)
    print(f"  Documents directory : {settings.DOCUMENTS_DIR}")
    print(f"  ChromaDB directory  : {settings.CHROMA_PERSIST_DIR}")
    print(f"  Collection name     : {settings.CHROMA_COLLECTION_NAME}")
    print(f"  Embedding model     : {settings.EMBEDDING_MODEL}")
    print(f"  Chunk size          : {settings.CHUNK_SIZE}")
    print(f"  Chunk overlap       : {settings.CHUNK_OVERLAP}")
    print("=" * 60 + "\n")

    start_time = time.time()

    # Step 1: Load documents
    print("[1/4] Loading documents...")
    docs = load_documents()
    if not docs:
        print("\n  [!] No documents found. Please add files to:", settings.DOCUMENTS_DIR)
        print("      Supported formats: .pdf, .txt, .md, .markdown\n")
        return
    print(f"      [OK] Loaded {len(docs)} page(s) / document(s).\n")

    # Step 2: Split documents into chunks
    print("[2/4] Splitting into chunks...")
    chunks = split_documents(docs)
    print(f"      [OK] Created {len(chunks)} chunk(s).\n")

    # Step 3: Initialize embedding model
    print("[3/4] Loading embedding model (first run downloads the model)...")
    embeddings = get_embeddings()
    print("      [OK] Embedding model ready.\n")

    # Step 4: Store in ChromaDB
    print("[4/4] Storing embeddings in ChromaDB...")

    # Reset singleton so ingest always writes fresh
    VectorStoreManager.reset()

    try:
        from langchain_chroma import Chroma
    except ImportError:
        from langchain_community.vectorstores import Chroma

    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

    # Add documents in batches for large document sets
    batch_size = 100
    total_added = 0
    vector_store = None

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i: i + batch_size]
        if i == 0:
            # Create or overwrite collection on first batch
            vector_store = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                collection_name=settings.CHROMA_COLLECTION_NAME,
                persist_directory=settings.CHROMA_PERSIST_DIR,
            )
        else:
            vector_store.add_documents(batch)
        total_added += len(batch)
        print(f"      Stored {total_added}/{len(chunks)} chunks...")

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("  INGESTION COMPLETE")
    print("=" * 60)
    print(f"  Documents loaded    : {len(docs)}")
    print(f"  Chunks created      : {len(chunks)}")
    print(f"  Embeddings stored   : {total_added}")
    print(f"  ChromaDB location   : {settings.CHROMA_PERSIST_DIR}")
    print(f"  Time elapsed        : {elapsed:.2f}s")
    print("=" * 60 + "\n")
    print("  [DONE] Documents are ready. Start the API and test with POST /chat.\n")


if __name__ == "__main__":
    run_ingestion()
