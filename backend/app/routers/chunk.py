"""
Chunk processing router.

Responsibilities:
  - Validate the incoming chunk request (technique name, text)
  - Execute the chunker engine
  - Persist the result to PostgreSQL
  - Return structured response
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..chunkers import CHUNKER_REGISTRY
from ..database import get_db
from ..models import ChunkingResult
from ..schemas import ChunkRequest, ChunkResponse, ChunkStats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chunk"])


# ─── Validation helpers ──────────────────────────────────────────────────────

def _validate_technique(technique: str) -> None:
    """Raise HTTP 400 if the technique name is not in the registry."""
    if technique not in CHUNKER_REGISTRY:
        available = list(CHUNKER_REGISTRY.keys())
        logger.warning("Invalid technique requested: '%s'. Available: %s", technique, available)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown chunking technique: '{technique}'. Available: {available}",
        )


def _validate_text(text: str) -> None:
    """Raise HTTP 400 if the input text is empty."""
    if not text or not text.strip():
        logger.warning("Empty text submitted for chunking.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text cannot be empty.",
        )


# ─── Service helpers ─────────────────────────────────────────────────────────

def _execute_chunker(technique: str, text: str, params: dict) -> dict:
    """Instantiate the chunker and run it with timing. Returns the raw result dict."""
    chunker_cls = CHUNKER_REGISTRY[technique]
    chunker = chunker_cls()
    logger.info("Executing technique '%s' with params %s on %d chars", technique, params or "defaults", len(text))

    try:
        result = chunker.chunk_timed(text, **params)
    except Exception as e:
        logger.error("Chunker '%s' raised an exception: %s", technique, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing technique '{technique}': {e}",
        ) from e

    logger.info(
        "Technique '%s' produced %d chunks in %.1fms",
        technique, result["stats"]["total_chunks"], result["processing_time_ms"],
    )
    return result


async def _persist_result(
    db: AsyncSession,
    technique: str,
    text: str,
    source_type: str,
    source_name: str | None,
    params: dict,
    chunks: list[str],
    stats: dict,
    processing_time_ms: float,
) -> ChunkingResult:
    """Save the chunking result to the database and return the ORM object."""
    db_result = ChunkingResult(
        technique=technique,
        input_preview=text[:200],
        source_type=source_type,
        source_name=source_name,
        parameters=params,
        chunks=chunks,
        total_chunks=stats["total_chunks"],
        avg_chunk_size=stats["avg_chunk_size"],
        processing_time_ms=processing_time_ms,
        total_characters=stats["total_characters"],
    )

    try:
        db.add(db_result)
        await db.commit()
        await db.refresh(db_result)
        logger.info("Persisted chunking result id=%d for technique '%s'", db_result.id, technique)
    except Exception as e:
        await db.rollback()
        logger.error("Failed to persist chunking result: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save result to database: {e}",
        ) from e

    return db_result


# ─── Route ────────────────────────────────────────────────────────────────────

@router.post("/chunk", response_model=ChunkResponse)
async def process_chunk(
    request: ChunkRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process text with the specified chunking technique and save results to PostgreSQL.
    """
    logger.info(
        "POST /api/chunk — technique=%s, source=%s, text_length=%d",
        request.technique, request.source_type, len(request.text),
    )

    # 1. Validate
    _validate_technique(request.technique)
    _validate_text(request.text)

    # 2. Execute
    result = _execute_chunker(request.technique, request.text, request.params)
    chunks = result["chunks"]
    stats = result["stats"]
    processing_time_ms = result["processing_time_ms"]

    # 3. Persist
    db_result = await _persist_result(
        db=db,
        technique=request.technique,
        text=request.text,
        source_type=request.source_type,
        source_name=request.source_name,
        params=request.params,
        chunks=chunks,
        stats=stats,
        processing_time_ms=processing_time_ms,
    )

    # 4. Respond
    return ChunkResponse(
        id=db_result.id,
        technique=request.technique,
        chunks=chunks,
        stats=ChunkStats(**stats),
        processing_time_ms=processing_time_ms,
        source_type=request.source_type,
        source_name=request.source_name,
    )
