"""File service for file upload and management."""

import os
import uuid
import aiofiles
from datetime import datetime
from typing import Optional
from pathlib import Path

from app.schemas.file import FileUploadResponse
from app.utils.logger import log_event


# Allowed file types and their extensions
ALLOWED_EXTENSIONS = {
    'application/pdf': ['.pdf'],
    'application/postscript': ['.ai', '.eps'],
    'image/vnd.adobe.photoshop': ['.psd'],
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/svg+xml': ['.svg'],
}

# Maximum file size: 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024

# Upload directory
UPLOAD_DIR = Path("/app/uploads")


class FileService:
    """Service for handling file uploads."""
    
    def __init__(self):
        # Ensure upload directory exists
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    def _validate_file_type(self, content_type: str, filename: str) -> bool:
        """Validate file type by MIME type and extension."""
        if content_type not in ALLOWED_EXTENSIONS:
            return False
        
        ext = Path(filename).suffix.lower()
        return ext in ALLOWED_EXTENSIONS.get(content_type, [])
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename to prevent collisions."""
        ext = Path(original_filename).suffix.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{timestamp}_{unique_id}{ext}"
    
    async def upload_design_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        user_id: str,
    ) -> FileUploadResponse:
        """Upload a design file."""
        # Validate file size
        file_size = len(file_content)
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum allowed ({MAX_FILE_SIZE / 1024 / 1024}MB)")
        
        # Validate file type
        if not self._validate_file_type(content_type, filename):
            raise ValueError(
                f"Invalid file type. Allowed types: PDF, AI, PSD, PNG, JPG, SVG"
            )
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(filename)
        
        # Create user upload directory
        user_upload_dir = UPLOAD_DIR / "designs" / user_id
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = user_upload_dir / unique_filename
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Generate URL (in production, this would be S3 URL or CDN)
        file_url = f"/files/designs/{user_id}/{unique_filename}"
        
        log_event(
            event_type="file.uploaded",
            user_id=user_id,
            filename=unique_filename,
            original_filename=filename,
            file_size=file_size,
            content_type=content_type,
        )
        
        return FileUploadResponse(
            filename=filename,
            file_url=file_url,
            file_size=file_size,
            content_type=content_type,
        )
    
    async def get_file_path(self, file_url: str) -> Optional[Path]:
        """Get actual file path from URL."""
        # Extract path from URL
        if file_url.startswith("/files/"):
            relative_path = file_url[7:]  # Remove "/files/"
            file_path = UPLOAD_DIR / relative_path
            if file_path.exists():
                return file_path
        return None
    
    async def delete_file(self, file_url: str) -> bool:
        """Delete a file."""
        file_path = await self.get_file_path(file_url)
        if file_path and file_path.exists():
            file_path.unlink()
            log_event(
                event_type="file.deleted",
                file_url=file_url,
            )
            return True
        return False





