"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ─── Chunk Request ────────────────────────────────────────────────────────────

class ChunkRequest(BaseModel):
    technique: str = Field(..., description="Chunker name from the registry")
    text: str = Field(..., min_length=1, description="Text to chunk")
    params: dict[str, Any] = Field(default_factory=dict, description="Technique-specific parameters")
    source_type: str = Field(default="custom", description="'preset' | 'custom' | 'upload'")
    source_name: str | None = Field(default=None, description="Preset name or filename")


# ─── Chunk Response ───────────────────────────────────────────────────────────

class ChunkStats(BaseModel):
    total_chunks: int
    total_characters: int
    avg_chunk_size: float
    min_chunk_size: int
    max_chunk_size: int


class ChunkResponse(BaseModel):
    id: int
    technique: str
    chunks: list[str]
    stats: ChunkStats
    processing_time_ms: float
    source_type: str
    source_name: str | None


# ─── Technique Info ───────────────────────────────────────────────────────────

class TechniqueParameter(BaseModel):
    name: str
    type: str
    default: Any
    description: str
    min: float | None = None
    max: float | None = None
    options: list[str] | None = None


class TechniqueInfo(BaseModel):
    name: str
    description: str
    category: str
    use_cases: list[str]
    parameters: list[dict[str, Any]]


# ─── Preset ───────────────────────────────────────────────────────────────────

class PresetInfo(BaseModel):
    name: str
    label: str
    description: str
    preview: str  # First 100 chars


class PresetDetail(BaseModel):
    name: str
    label: str
    text: str


# ─── Upload Response ──────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    filename: str
    extension: str
    text: str
    character_count: int
    parser_used: str


# ─── History ──────────────────────────────────────────────────────────────────

class HistoryItem(BaseModel):
    id: int
    technique: str
    input_preview: str
    source_type: str
    source_name: str | None
    parameters: dict[str, Any]
    total_chunks: int
    avg_chunk_size: float
    processing_time_ms: float
    total_characters: int
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryDetail(HistoryItem):
    chunks: list[str]
