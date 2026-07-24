from fastapi import APIRouter, File, HTTPException, UploadFile, status
from ..file_parser import FileParser
from ..schemas import UploadResponse

router = APIRouter(prefix="/api", tags=["upload"])
file_parser = FileParser()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document (PDF, DOCX, TXT, MD, CSV, JSON, HTML, PNG, JPG, TIFF)
    and return extracted structured Markdown text.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    content = await file.read()
    file_size = len(content)

    try:
        parsed_result = await file_parser.parse(
            filename=file.filename,
            content=content,
            file_size=file_size,
        )
        return UploadResponse(**parsed_result)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}",
        )
