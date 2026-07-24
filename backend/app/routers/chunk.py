from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..chunkers import CHUNKER_REGISTRY
from ..database import get_db
from ..models import ChunkingResult
from ..schemas import ChunkRequest, ChunkResponse, ChunkStats

router = APIRouter(prefix="/api", tags=["chunk"])


@router.post("/chunk", response_model=ChunkResponse)
async def process_chunk(
    request: ChunkRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process text with the specified chunking technique and save results to PostgreSQL.
    """
    if request.technique not in CHUNKER_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown chunking technique: '{request.technique}'. Available: {list(CHUNKER_REGISTRY.keys())}",
        )

    chunker_cls = CHUNKER_REGISTRY[request.technique]
    chunker = chunker_cls()

    try:
        res = chunker.chunk_timed(request.text, **request.params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing technique '{request.technique}': {str(e)}",
        )

    chunks = res["chunks"]
    stats_dict = res["stats"]
    processing_time_ms = res["processing_time_ms"]

    # Save result to database
    db_result = ChunkingResult(
        technique=request.technique,
        input_preview=request.text[:200],
        source_type=request.source_type,
        source_name=request.source_name,
        parameters=request.params,
        chunks=chunks,
        total_chunks=stats_dict["total_chunks"],
        avg_chunk_size=stats_dict["avg_chunk_size"],
        processing_time_ms=processing_time_ms,
        total_characters=stats_dict["total_characters"],
    )
    db.add(db_result)
    await db.commit()
    await db.refresh(db_result)

    return ChunkResponse(
        id=db_result.id,
        technique=request.technique,
        chunks=chunks,
        stats=ChunkStats(**stats_dict),
        processing_time_ms=processing_time_ms,
        source_type=request.source_type,
        source_name=request.source_name,
    )
