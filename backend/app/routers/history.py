"""
History router — CRUD operations for past chunking runs.

Responsibilities:
  - List history (paginated)
  - Get single history detail with full chunks
  - Delete a history entry
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import ChunkingResult
from ..schemas import HistoryDetail, HistoryItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["history"])


# ─── Validation helpers ──────────────────────────────────────────────────────

def _validate_limit(limit: int) -> int:
    """Clamp the limit parameter to a safe range [1, 200]."""
    clamped = max(1, min(limit, 200))
    if clamped != limit:
        logger.debug("History limit clamped from %d to %d", limit, clamped)
    return clamped


async def _get_history_item_or_404(db: AsyncSession, item_id: int) -> ChunkingResult:
    """Fetch a history item by ID or raise HTTP 404."""
    logger.debug("Looking up history item id=%d", item_id)
    try:
        stmt = select(ChunkingResult).where(ChunkingResult.id == item_id)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()
    except Exception as e:
        logger.error("Database query failed for history item id=%d: %s", item_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching history item #{item_id}: {e}",
        ) from e

    if not item:
        logger.warning("History item id=%d not found", item_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History item #{item_id} not found.",
        )
    return item


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("/history", response_model=list[HistoryItem])
async def get_history(
    limit: int = Query(default=50, ge=1, le=200, description="Max items to return"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve history of chunking runs ordered by most recent."""
    safe_limit = _validate_limit(limit)
    logger.info("GET /api/history — limit=%d", safe_limit)

    try:
        stmt = (
            select(ChunkingResult)
            .order_by(ChunkingResult.created_at.desc())
            .limit(safe_limit)
        )
        result = await db.execute(stmt)
        items = result.scalars().all()
        logger.info("Returning %d history items", len(items))
        return items
    except Exception as e:
        logger.error("Failed to fetch history: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {e}",
        ) from e


@router.get("/history/{item_id}", response_model=HistoryDetail)
async def get_history_detail(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed history item including full chunks."""
    logger.info("GET /api/history/%d — fetching detail", item_id)
    item = await _get_history_item_or_404(db, item_id)
    logger.info("Returning history detail id=%d — technique=%s, %d chunks", item.id, item.technique, item.total_chunks)
    return item


@router.delete("/history/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a history item."""
    logger.info("DELETE /api/history/%d", item_id)
    item = await _get_history_item_or_404(db, item_id)

    try:
        await db.delete(item)
        await db.commit()
        logger.info("Deleted history item id=%d (technique=%s)", item_id, item.technique)
    except Exception as e:
        await db.rollback()
        logger.error("Failed to delete history item id=%d: %s", item_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete history item #{item_id}: {e}",
        ) from e
