"""File upload API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from fastapi.responses import FileResponse
from uuid import UUID
from pathlib import Path

from app.core.rate_limit import limiter, RateLimits
from app.schemas.file import FileUploadResponse, TemplateImageUploadResponse, FontUploadResponse
from app.services.file_service import FileService, MAX_FILE_SIZE, MAX_TEMPLATE_IMAGE_SIZE, MAX_FONT_FILE_SIZE, UPLOAD_DIR
from app.api.deps import get_current_admin_user

router = APIRouter()


@router.post(
    "/files/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload design file",
    description=f"Upload a design file (PDF, AI, PSD, PNG, JPG, SVG). Max size: {MAX_FILE_SIZE / 1024 / 1024}MB",
)
@limiter.limit(RateLimits.FILE_UPLOAD)
async def upload_file(
    request: Request,
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


@router.post(
    "/placeholder-images/upload",
    response_model=TemplateImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload placeholder image",
    description=f"Upload an image for template placeholder (PNG, JPG, WEBP). Max size: {MAX_TEMPLATE_IMAGE_SIZE / 1024 / 1024}MB",
)
@limiter.limit(RateLimits.FILE_UPLOAD)
async def upload_placeholder_image(
    request: Request,
    file: UploadFile = File(..., description="Placeholder image file"),
) -> TemplateImageUploadResponse:
    """Upload a placeholder image for order templates."""
    # Read file content
    content = await file.read()
    
    service = FileService()
    try:
        return await service.upload_template_image(
            file_content=content,
            filename=file.filename or "placeholder.png",
            content_type=file.content_type or "image/png",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/templates/upload",
    response_model=TemplateImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload template image",
    description=f"Upload a template image (PNG, JPG, WEBP). Max size: {MAX_TEMPLATE_IMAGE_SIZE / 1024 / 1024}MB",
)
@limiter.limit(RateLimits.FILE_UPLOAD)
async def upload_template_image(
    request: Request,
    file: UploadFile = File(..., description="Template image file"),
    _: dict = Depends(get_current_admin_user),
) -> TemplateImageUploadResponse:
    """Upload a template image. Admin only."""
    # Read file content
    content = await file.read()
    
    service = FileService()
    try:
        return await service.upload_template_image(
            file_content=content,
            filename=file.filename or "template.png",
            content_type=file.content_type or "image/png",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/files/templates/{filename}",
    summary="Get template image",
    description="Download a template image",
)
async def get_template_file(
    filename: str,
) -> FileResponse:
    """Get a template image file."""
    file_path = UPLOAD_DIR / "templates" / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
    )


@router.get(
    "/files/receipts/{filename}",
    summary="Get receipt image",
    description="Download a payment receipt image",
)
async def get_receipt_file(
    filename: str,
) -> FileResponse:
    """Get a receipt image file."""
    file_path = UPLOAD_DIR / "receipts" / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
    )


@router.post(
    "/fonts/upload",
    response_model=FontUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload font file",
    description=f"Upload a font file (TTF, WOFF, WOFF2). Max size: {MAX_FONT_FILE_SIZE / 1024 / 1024}MB",
)
@limiter.limit(RateLimits.FILE_UPLOAD)
async def upload_font_file(
    request: Request,
    file: UploadFile = File(..., description="Font file"),
    _: dict = Depends(get_current_admin_user),
) -> FontUploadResponse:
    """Upload a font file. Admin only."""
    # Read file content
    content = await file.read()
    
    service = FileService()
    try:
        result = await service.upload_font_file(
            file_content=content,
            filename=file.filename or "font.ttf",
            content_type=file.content_type or "application/octet-stream",
        )
        return FontUploadResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/files/fonts/{filename}",
    summary="Get font file",
    description="Download a font file",
)
async def get_font_file(
    filename: str,
) -> FileResponse:
    """Get a font file."""
    file_path = UPLOAD_DIR / "fonts" / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Set correct content type based on extension
    ext = file_path.suffix.lower()
    content_types = {
        '.ttf': 'font/ttf',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
    }
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=content_types.get(ext, 'application/octet-stream'),
    )


@router.get(
    "/files/previews/{filename}",
    summary="Get preview image",
    description="Download a generated preview image",
)
async def get_preview_file(
    filename: str,
) -> FileResponse:
    """Get a generated preview image file."""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
    )

