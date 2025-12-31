"""File upload API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from uuid import UUID
from pathlib import Path

from app.schemas.file import FileUploadResponse
from app.services.file_service import FileService, MAX_FILE_SIZE, UPLOAD_DIR

router = APIRouter()


@router.post(
    "/files/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload design file",
    description=f"Upload a design file (PDF, AI, PSD, PNG, JPG, SVG). Max size: {MAX_FILE_SIZE / 1024 / 1024}MB",
)
async def upload_file(
    file: UploadFile = File(..., description="Design file to upload"),
    user_id: UUID = Query(..., description="User ID"),
) -> FileUploadResponse:
    """Upload a design file."""
    # Read file content
    content = await file.read()
    
    service = FileService()
    try:
        return await service.upload_design_file(
            file_content=content,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            user_id=str(user_id),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/files/designs/{user_id}/{filename}",
    summary="Get design file",
    description="Download a design file",
)
async def get_file(
    user_id: str,
    filename: str,
) -> FileResponse:
    """Get a design file."""
    file_path = UPLOAD_DIR / "designs" / user_id / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
    )


@router.delete(
    "/files/designs/{user_id}/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete design file",
    description="Delete a design file",
)
async def delete_file(
    user_id: str,
    filename: str,
    requesting_user_id: UUID = Query(..., description="Requesting user ID"),
) -> None:
    """Delete a design file."""
    # Verify user owns the file
    if str(requesting_user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    file_url = f"/files/designs/{user_id}/{filename}"
    service = FileService()
    
    success = await service.delete_file(file_url)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )



