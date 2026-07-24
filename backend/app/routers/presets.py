"""
Presets router — read-only access to sample input texts.

Responsibilities:
  - List available presets with previews
  - Return full preset text by name
"""
import logging
from fastapi import APIRouter, HTTPException, status

from ..presets import get_preset, list_presets
from ..schemas import PresetDetail, PresetInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["presets"])


@router.get("/presets", response_model=list[PresetInfo])
async def get_presets_list():
    """List available preset input texts."""
    logger.info("GET /api/presets — listing all presets")
    try:
        presets = list_presets()
        logger.info("Returning %d presets", len(presets))
        return presets
    except Exception as e:
        logger.error("Failed to list presets: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load presets: {e}",
        ) from e


def _validate_preset_exists(name: str) -> dict:
    """Fetch a preset by name or raise HTTP 404."""
    preset = get_preset(name)
    if not preset:
        logger.warning("Preset '%s' not found", name)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{name}' not found. Use GET /api/presets to list available presets.",
        )
    return preset


@router.get("/presets/{name}", response_model=PresetDetail)
async def get_preset_detail(name: str):
    """Get full preset text by name."""
    logger.info("GET /api/presets/%s — fetching detail", name)

    preset = _validate_preset_exists(name)
    logger.info("Returning preset '%s' — %d chars", name, len(preset["text"]))

    return PresetDetail(
        name=name,
        label=preset["label"],
        text=preset["text"],
    )
