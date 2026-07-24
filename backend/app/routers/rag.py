"""
RAG API Router — endpoints for SSE ingestion stream, QA chat, and strategy catalogs.
"""
import json
import logging
import uuid
from typing import Any
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..retrievers import RETRIEVER_REGISTRY
from ..services.rag_service import (
    AVAILABLE_OPENROUTER_MODELS,
    generate_rag_answer,
    run_ingestion_pipeline_stream,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["rag"])


class RagChatRequest(BaseModel):
    query: str
    model_id: str = "google/gemini-2.0-flash-001"
    retrieval_technique: str = "dense"
    session_id: str | None = None
    limit: int = 4


@router.get("/models")
async def list_models():
    """Return available OpenRouter LLM models for the UI dropdown."""
    return {"models": AVAILABLE_OPENROUTER_MODELS}


@router.get("/retrievers")
async def list_retrievers():
    """Return available RAG retrieval strategies."""
    retrievers = []
    for name, cls in RETRIEVER_REGISTRY.items():
        instance = cls()
        retrievers.append(instance.get_info())
    return {"retrievers": retrievers}


@router.post("/pipeline-stream")
async def pipeline_stream(
    files: list[UploadFile] = File(...),
    chunk_technique: str = Form("semantic_chunker"),
    chunk_params_json: str = Form("{}"),
    session_id: str = Form(None),
):
    """
    Multipart file upload endpoint that streams real-time SSE progress events
    for Parsing ➔ Chunking ➔ 512d CLIP Embedding ➔ Qdrant Indexing.
    """
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded.")

    sid = session_id or str(uuid.uuid4())
    try:
        params = json.loads(chunk_params_json)
    except Exception:
        params = {}

    file_items = []
    for f in files:
        content = await f.read()
        file_items.append({
            "filename": f.filename or "file",
            "content": content,
        })

    logger.info("Starting SSE RAG Ingestion Stream for %d file(s), session=%s", len(file_items), sid)

    generator = run_ingestion_pipeline_stream(
        files=file_items,
        chunk_technique=chunk_technique,
        chunk_params=params,
        session_id=sid,
    )

    return StreamingResponse(generator, media_type="text/event-stream")


@router.post("/chat")
async def rag_chat(request: RagChatRequest):
    """
    RAG QA Chat endpoint — runs chosen retriever against Qdrant, calls OpenRouter API,
    and returns synthesized answer along with source context for the UI inspector.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    try:
        result = await generate_rag_answer(
            query=request.query,
            retrieval_technique=request.retrieval_technique,
            model_id=request.model_id,
            session_id=request.session_id,
            limit=request.limit,
        )
        return result
    except Exception as e:
        logger.error("RAG chat endpoint error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG QA failed: {str(e)}",
        ) from e
