from fastapi import APIRouter, HTTPException, status
from ..presets import get_preset, list_presets
from ..schemas import PresetDetail, PresetInfo

router = APIRouter(prefix="/api", tags=["presets"])


@router.get("/presets", response_model=list[PresetInfo])
async def get_presets_list():
    """List available preset input texts."""
    return list_presets()


@router.get("/presets/{name}", response_model=PresetDetail)
async def get_preset_detail(name: str):
    """Get full preset text by name."""
    preset = get_preset(name)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{name}' not found.",
        )
    return PresetDetail(
        name=name,
        label=preset["label"],
        text=preset["text"],
    )
