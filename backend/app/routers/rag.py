"""
RAG API Router — endpoints for SSE ingestion stream, QA chat, and strategy catalogs.
All endpoints require a valid JWT token (Authorization: Bearer <token>).
"""
import json
import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..crypto import decrypt
from ..database import get_db
from ..models import User, UserCredentials
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


async def _resolve_user_creds(
    current_user: User,
    db: AsyncSession,
) -> dict | None:
    """
    Return decrypted user credentials dict or None (admin uses .env).
    Raises 403 if regular user has no credentials configured.
    """
    if current_user.is_admin:
        return None  # Admin — use .env settings in rag_service

    result = await db.execute(
        select(UserCredentials).where(UserCredentials.user_id == current_user.id)
    )
    creds = result.scalar_one_or_none()

    if not creds or not creds.qdrant_url_enc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API credentials not configured. Please add your Qdrant and OpenRouter keys in Settings.",
        )

    return {
        "user_id": current_user.id,
        "qdrant_url": decrypt(creds.qdrant_url_enc),
        "qdrant_api_key": decrypt(creds.qdrant_api_key_enc),
        "openrouter_api_key": decrypt(creds.openrouter_api_key_enc),
        "qdrant_collection_name": creds.qdrant_collection_name or f"rag_{current_user.id}",
    }


@router.get("/models")
async def list_models(current_user: User = Depends(get_current_user)):
    """Return available OpenRouter LLM models for the UI dropdown."""
    return {"models": AVAILABLE_OPENROUTER_MODELS}


@router.get("/retrievers")
async def list_retrievers(current_user: User = Depends(get_current_user)):
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Multipart file upload endpoint that streams real-time SSE progress events
    for Parsing ➔ Chunking ➔ 512d CLIP Embedding ➔ Qdrant Indexing.
    Uses per-user credentials for multi-tenant Qdrant isolation.
    """
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded.")

    user_creds = await _resolve_user_creds(current_user, db)

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

    logger.info(
        "Starting SSE RAG Ingestion Stream for %d file(s), session=%s, user=%d",
        len(file_items), sid, current_user.id,
    )

    generator = run_ingestion_pipeline_stream(
        files=file_items,
        chunk_technique=chunk_technique,
        chunk_params=params,
        session_id=sid,
        user_creds=user_creds,
    )

    return StreamingResponse(generator, media_type="text/event-stream")


@router.post("/chat")
async def rag_chat(
    request: RagChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    RAG QA Chat endpoint — runs chosen retriever against user's Qdrant collection,
    calls OpenRouter API, and returns synthesized answer with source context.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    user_creds = await _resolve_user_creds(current_user, db)

    try:
        result = await generate_rag_answer(
            query=request.query,
            retrieval_technique=request.retrieval_technique,
            model_id=request.model_id,
            session_id=request.session_id,
            limit=request.limit,
            user_creds=user_creds,
        )
        return result
    except Exception as e:
        logger.error("RAG chat endpoint error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG QA failed: {str(e)}",
        ) from e
