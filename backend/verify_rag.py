"""Verification script for ChromaDB persistence and retriever output."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from app.rag.vector_store import get_vector_store
from app.rag.retriever import retrieve, retrieve_with_scores, format_context

print("=== Verification 2: ChromaDB Persistence ===")
store = get_vector_store()
count = store._collection.count()
print(f"Documents in ChromaDB collection: {count}")

print()
print("=== Verification 3: Retriever Output ===")
query = "What is the learning budget policy for employees?"
print(f"Query: {query}")
print()

results = retrieve_with_scores(query, k=3)
for i, (doc, score) in enumerate(results):
    filename = doc.metadata.get("filename", "unknown")
    page = doc.metadata.get("page", "N/A")
    snippet = doc.page_content[:120].replace("\n", " ")
    print(f"[{i+1}] Score: {score:.4f} | Source: {filename} | Page: {page}")
    print(f"     Snippet: {snippet}...")
    print()

print("=== Formatted Context for LLM (first 600 chars) ===")
docs = [d for d, _ in results]
ctx = format_context(docs)
print(ctx[:600])
print("...")
