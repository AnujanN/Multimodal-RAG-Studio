"""
File upload router.

Responsibilities:
  - Validate uploaded file (filename exists, size within limits)
  - Delegate parsing to FileParser
  - Return extracted text with metadata
"""
import logging
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ..file_parser import FileParser
from ..schemas import UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])
file_parser = FileParser()


# ─── Validation helpers ──────────────────────────────────────────────────────

def _validate_upload(file: UploadFile) -> None:
    """Raise HTTP 400 if the uploaded file is invalid."""
    if not file.filename:
        logger.warning("Upload rejected: no filename provided.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )


async def _read_file_content(file: UploadFile) -> tuple[bytes, int]:
    """Read file content and return (bytes, size). Logs the read operation."""
    try:
        content = await file.read()
        file_size = len(content)
        logger.info(
            "Read uploaded file '%s' — %d bytes (%.2f MB)",
            file.filename, file_size, file_size / (1024 * 1024),
        )
        return content, file_size
    except Exception as e:
        logger.error("Failed to read uploaded file '%s': %s", file.filename, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read uploaded file: {e}",
        ) from e


# ─── Route ────────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document (PDF, DOCX, TXT, MD, CSV, JSON, HTML, PNG, JPG, TIFF)
    and return extracted structured Markdown text.
    """
    logger.info("POST /api/upload — filename=%s, content_type=%s", file.filename, file.content_type)

    # 1. Validate
    _validate_upload(file)

    # 2. Read content
    content, file_size = await _read_file_content(file)

    # 3. Parse
    try:
        parsed_result = await file_parser.parse(
            filename=file.filename,
            content=content,
            file_size=file_size,
        )
        logger.info(
            "Parsed '%s' successfully — parser=%s, extracted %d chars",
            file.filename, parsed_result["parser_used"], parsed_result["character_count"],
        )
        return UploadResponse(**parsed_result)
    except ValueError as ve:
        logger.warning("Upload validation error for '%s': %s", file.filename, ve)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        ) from ve
    except Exception as e:
        logger.error("Upload processing failed for '%s': %s", file.filename, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file '{file.filename}': {e}",
        ) from e
