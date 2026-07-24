from fastapi import APIRouter
from ..chunkers import CHUNKER_REGISTRY

router = APIRouter(prefix="/api", tags=["techniques"])


@router.get("/techniques")
async def list_techniques():
    """Return all 21 chunking techniques grouped by category."""
    grouped = {"basic": [], "advanced": [], "ai_powered": []}

    for name, cls in CHUNKER_REGISTRY.items():
        instance = cls()
        info = instance.get_info()
        category = info.get("category", "basic")
        if category in grouped:
            grouped[category].append(info)
        else:
            grouped.setdefault(category, []).append(info)

    return {
        "total": len(CHUNKER_REGISTRY),
        "categories": grouped,
    }
