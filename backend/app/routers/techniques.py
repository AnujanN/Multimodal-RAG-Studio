"""
Techniques router — lists all available chunking techniques.

Responsibilities:
  - Instantiate each registered chunker
  - Collect metadata grouped by category
  - Return structured response
"""
import logging
from fastapi import APIRouter, HTTPException, status

from ..chunkers import CHUNKER_REGISTRY

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["techniques"])


def _build_technique_catalog() -> dict:
    """Build the grouped technique catalog from the registry."""
    grouped: dict[str, list] = {"basic": [], "advanced": [], "ai_powered": []}

    for name, cls in CHUNKER_REGISTRY.items():
        try:
            instance = cls()
            info = instance.get_info()
            category = info.get("category", "basic")
            grouped.setdefault(category, []).append(info)
            logger.debug("Registered technique '%s' under category '%s'", name, category)
        except Exception as e:
            logger.error("Failed to load technique '%s': %s", name, e, exc_info=True)
            # Skip broken techniques rather than crashing the entire endpoint
            continue

    return grouped


@router.get("/techniques")
async def list_techniques():
    """Return all chunking techniques grouped by category."""
    logger.info("GET /api/techniques — building catalog from %d registered chunkers", len(CHUNKER_REGISTRY))

    try:
        grouped = _build_technique_catalog()
        total = sum(len(v) for v in grouped.values())
        logger.info("Returning %d techniques across %d categories", total, len(grouped))

        return {
            "total": total,
            "categories": grouped,
        }
    except Exception as e:
        logger.error("Failed to build technique catalog: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load techniques: {e}",
        ) from e
