"""RAG Pipeline Module — Orchestrates Retrieve → Prompt → Generate."""

import time
from typing import Optional
from app.rag.retriever import retrieve, format_context
from app.llm.ollama_client import OllamaClientManager
from app.utils.logger import logger


RAG_SYSTEM_PROMPT = """You are an expert AI Workforce Assistant for a Tata Steel enterprise platform.

You answer questions about company HR policies, training programs, skill frameworks, 
promotion policies, safety manuals, and workforce development.

IMPORTANT RULES:
1. Answer ONLY using the information provided in the retrieved context below.
2. If the answer is not found in the context, say clearly:
   "I don't have specific information about that in the company documents. Please contact HR directly."
3. Always cite the document source (e.g., "According to HR_Policy.pdf...").
4. Be professional, concise, and accurate.
5. Do NOT invent, assume, or hallucinate any company-specific details.

Retrieved Company Knowledge:
{context}
"""


def rag_answer(question: str, k: int = None) -> str:
    """Execute the full RAG pipeline for a given user question.

    Workflow:
        1. Retrieve top-k relevant chunks from ChromaDB.
        2. Format chunks into a structured context string.
        3. Inject context into the RAG system prompt.
        4. Pass to Qwen2.5:7b via Ollama.
        5. Return the grounded answer.

    Args:
        question (str): User question.
        k (int, optional): Number of documents to retrieve. Defaults to settings.TOP_K.

    Returns:
        str: Grounded answer from Qwen2.5:7b.
    """
    # Step 1: Retrieve relevant documents
    docs = retrieve(query=question, k=k)

    # Step 2: Format context
    context = format_context(docs)

    # Step 3: Build messages
    system_message = RAG_SYSTEM_PROMPT.format(context=context)

    messages = [
        ("system", system_message),
        ("human", question),
    ]

    # Step 4: Invoke LLM and measure time
    try:
        llm = OllamaClientManager.get_client()
        start_time = time.time()
        response = llm.invoke(messages)
        elapsed = time.time() - start_time
        logger.info(f"LLM response time: {elapsed:.2f}s")

        answer = response.content if hasattr(response, "content") else str(response)
        return answer

    except Exception as e:
        logger.error(f"RAG pipeline LLM error: {e}")
        return (
            "I encountered an error retrieving the answer from company documents. "
            "Please try again or contact HR directly."
        )
