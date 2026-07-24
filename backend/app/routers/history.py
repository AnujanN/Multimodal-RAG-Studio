from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import ChunkingResult
from ..schemas import HistoryDetail, HistoryItem

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=list[HistoryItem])
async def get_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve history of chunking runs ordered by most recent."""
    stmt = (
        select(ChunkingResult)
        .order_by(ChunkingResult.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items


@router.get("/history/{item_id}", response_model=HistoryDetail)
async def get_history_detail(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed history item including full chunks."""
    stmt = select(ChunkingResult).where(ChunkingResult.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History item #{item_id} not found.",
        )
    return item


@router.delete("/history/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a history item."""
    stmt = select(ChunkingResult).where(ChunkingResult.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History item #{item_id} not found.",
        )
    await db.delete(item)
    await db.commit()
