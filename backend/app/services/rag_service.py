"""
RAG Service Layer — Streams ingestion pipeline via SSE and synthesizes QA via OpenRouter API.
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Any
import httpx

from ..chunkers import CHUNKER_REGISTRY
from ..config import settings
from ..embeddings import embedder
from ..file_parser import FileParser
from ..qdrant_service import qdrant_service
from ..retrievers import get_retriever

logger = logging.getLogger(__name__)

file_parser = FileParser()

# Curated list of top OpenRouter models for UI dropdown
AVAILABLE_OPENROUTER_MODELS = [
    {
        "id": "google/gemini-2.0-flash-001",
        "name": "Gemini 2.0 Flash (Fast, Vision)",
        "provider": "Google",
        "supports_vision": True,
    },
    {
        "id": "meta-llama/llama-3.3-70b-instruct",
        "name": "Llama 3.3 70B Instruct",
        "provider": "Meta",
        "supports_vision": False,
    },
    {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "OpenAI",
        "supports_vision": True,
    },
    {
        "id": "anthropic/claude-3.5-haiku",
        "name": "Claude 3.5 Haiku",
        "provider": "Anthropic",
        "supports_vision": False,
    },
]


async def run_ingestion_pipeline_stream(
    files: list[dict[str, Any]],  # [{"filename": str, "content": bytes}]
    chunk_technique: str,
    chunk_params: dict,
    session_id: str,
) -> AsyncGenerator[str, None]:
    """
    Server-Sent Events (SSE) generator streaming ingestion progress steps.
    Step 1: Document Parsing
    Step 2: Chunking
    Step 3: Dual 512d CLIP Embedding
    Step 4: Qdrant Indexing
    """
    logger.info("Starting SSE RAG Ingestion Pipeline for session '%s' (%d files, technique='%s')", session_id, len(files), chunk_technique)

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    try:
        # ── Step 1: Document Parsing ──────────────────────────────────────────
        yield sse("progress", {"step": "parsing", "message": f"Parsing {len(files)} document(s) with Docling OCR...", "progress": 25})
        await asyncio.sleep(0.3)

        parsed_texts = []
        for file_item in files:
            fname = file_item["filename"]
            content = file_item["content"]
            result = await file_parser.parse(filename=fname, content=content, file_size=len(content))
            parsed_texts.append({
                "filename": fname,
                "text": result["text"],
                "parser_used": result["parser_used"],
            })

        logger.info("Step 1 complete — parsed %d document(s).", len(parsed_texts))

        # ── Step 2: Text Chunking ─────────────────────────────────────────────
        yield sse("progress", {"step": "chunking", "message": f"Splitting text using '{chunk_technique}'...", "progress": 50})
        await asyncio.sleep(0.3)

        chunker_cls = CHUNKER_REGISTRY.get(chunk_technique)
        if not chunker_cls:
            raise ValueError(f"Unknown chunking technique: {chunk_technique}")

        chunker = chunker_cls()
        all_chunks = []
        payloads = []

        for p in parsed_texts:
            chunks = chunker.chunk(p["text"], **chunk_params)
            for i, c in enumerate(chunks):
                all_chunks.append(c)
                payloads.append({
                    "session_id": session_id,
                    "text": c,
                    "chunk_index": i,
                    "source_name": p["filename"],
                    "source_type": "text",
                    "technique": chunk_technique,
                })

        logger.info("Step 2 complete — created %d chunk(s).", len(all_chunks))

        if not all_chunks:
            yield sse("progress", {"step": "complete", "message": "No text extracted from documents.", "progress": 100})
            yield sse("done", {"session_id": session_id, "total_chunks": 0})
            return

        # ── Step 3: 512d CLIP Embedding ───────────────────────────────────────
        yield sse("progress", {"step": "embedding", "message": f"Generating 512d CLIP vectors for {len(all_chunks)} chunk(s)...", "progress": 75})
        await asyncio.sleep(0.3)

        vectors = embedder.embed_text_batch(all_chunks)
        logger.info("Step 3 complete — generated %d 512d CLIP vector(s).", len(vectors))

        # ── Step 4: Qdrant Indexing ───────────────────────────────────────────
        yield sse("progress", {"step": "indexing", "message": "Indexing vectors & payloads into Qdrant Cloud...", "progress": 95})
        await asyncio.sleep(0.3)

        indexed_count = qdrant_service.upsert_points(vectors=vectors, payloads=payloads)
        logger.info("Step 4 complete — indexed %d points in Qdrant.", indexed_count)

        yield sse("progress", {"step": "complete", "message": f"Successfully indexed {indexed_count} chunk(s) into Qdrant Cloud!", "progress": 100})
        yield sse("done", {"session_id": session_id, "total_chunks": indexed_count})

    except Exception as e:
        logger.error("RAG Pipeline error: %s", e, exc_info=True)
        yield sse("error", {"message": f"Ingestion pipeline failed: {str(e)}"})


async def generate_rag_answer(
    query: str,
    retrieval_technique: str,
    model_id: str,
    session_id: str | None = None,
    limit: int = 4,
) -> dict[str, Any]:
    """
    Run chosen retriever to fetch top chunks, then query OpenRouter API to generate answer.
    """
    logger.info("RAG QA Request — model=%s, retriever=%s, query='%s'", model_id, retrieval_technique, query[:50])

    # 1. Retrieve context chunks
    retriever = get_retriever(retrieval_technique)
    context_items = await retriever.retrieve(query=query, limit=limit, session_id=session_id)

    if not context_items:
        return {
            "answer": "No relevant context found in the uploaded documents. Please index some documents first.",
            "retrieved_context": [],
            "model_used": model_id,
            "retrieval_technique": retrieval_technique,
        }

    # 2. Build system prompt & context string
    context_str = "\n\n---\n\n".join([
        f"[Source: {item['source_name']} | Match Score: {item['score']}]\n{item['text']}"
        for item in context_items
    ])

    system_prompt = (
        "You are an expert RAG AI assistant. Answer the user's question accurately using ONLY "
        "the provided document context snippets below. If the context does not contain enough information, "
        "say so clearly. Always cite the document source names in your response."
    )

    user_message = f"DOCUMENT CONTEXT:\n{context_str}\n\nUSER QUESTION:\n{query}"

    # 3. Call OpenRouter API
    answer = "Error generating response from LLM."
    if settings.openrouter_api_key:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key.strip()}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_id,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "temperature": 0.3,
                    },
                )
                if resp.status_code == 200:
                    answer = resp.json()["choices"][0]["message"]["content"]
                    logger.info("OpenRouter response generated successfully (%d chars).", len(answer))
                else:
                    logger.error("OpenRouter API returned HTTP %d: %s", resp.status_code, resp.text)
                    answer = f"[OpenRouter API Error {resp.status_code}: {resp.text}]"
        except Exception as e:
            logger.error("Failed to connect to OpenRouter API: %s", e, exc_info=True)
            answer = f"[Connection error to OpenRouter: {str(e)}]"
    else:
        logger.warning("No OpenRouter API Key set in environment (.env). Synthesizing fallback offline summary.")
        answer = (
            "⚠️ **OpenRouter API Key not set in `.env`**\n\n"
            "Below are the top retrieved context chunks for your question:\n\n" + context_str
        )

    return {
        "answer": answer,
        "retrieved_context": context_items,
        "model_used": model_id,
        "retrieval_technique": retrieval_technique,
    }
