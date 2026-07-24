"""SQLAlchemy ORM models for PostgreSQL."""
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ChunkingResult(Base):
    """Stores every chunking operation result for the history panel."""

    __tablename__ = "chunking_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # What chunker was used
    technique: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Input metadata
    input_preview: Mapped[str] = mapped_column(Text, nullable=False)  # First 200 chars
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "preset"|"custom"|"upload"
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)  # preset name or filename

    # Parameters used
    parameters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default={})

    # Results
    chunks: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=[])
    total_chunks: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_chunk_size: Mapped[float] = mapped_column(Float, nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    total_characters: Mapped[int] = mapped_column(Integer, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
