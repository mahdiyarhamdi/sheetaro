"""File schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class FileUploadResponse(BaseModel):
    """Response schema for file upload."""
    filename: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="URL to access the file")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")


class FileInfo(BaseModel):
    """Schema for file information."""
    filename: str
    file_url: str
    file_size: int
    content_type: str
    created_at: Optional[str] = None


class TemplateImageUploadResponse(BaseModel):
    """Response schema for template image upload with dimensions."""
    filename: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="URL to access the file")
    preview_url: str = Field(..., description="URL for preview (same as file_url)")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")


class FontUploadResponse(BaseModel):
    """Response schema for font file upload."""
    filename: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="URL to access the font file")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")










