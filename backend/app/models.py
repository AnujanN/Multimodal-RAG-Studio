"""SQLAlchemy ORM models for PostgreSQL."""
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    """Registered application user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)  # None for Google OAuth users
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship to credentials
    credentials: Mapped["UserCredentials | None"] = relationship(
        "UserCredentials", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class UserCredentials(Base):
    """Per-user encrypted API credentials for Qdrant and OpenRouter."""

    __tablename__ = "user_credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Fernet-encrypted credential fields (store ciphertext as text)
    qdrant_url_enc: Mapped[str] = mapped_column(Text, nullable=False, default="")
    qdrant_api_key_enc: Mapped[str] = mapped_column(Text, nullable=False, default="")
    openrouter_api_key_enc: Mapped[str] = mapped_column(Text, nullable=False, default="")
    qdrant_collection_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Back-reference
    user: Mapped["User"] = relationship("User", back_populates="credentials")


class ChunkingResult(Base):
    """Stores every chunking operation result for the history panel."""

    __tablename__ = "chunking_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Optional user association (nullable for backward compatibility)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

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
