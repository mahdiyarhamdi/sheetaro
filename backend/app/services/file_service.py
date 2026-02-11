"""File service for file upload and management."""

import os
import uuid
import aiofiles
from datetime import datetime
from typing import Optional
from pathlib import Path
from io import BytesIO

from PIL import Image

from app.schemas.file import FileUploadResponse, TemplateImageUploadResponse
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

# Allowed image types for template uploads
ALLOWED_IMAGE_EXTENSIONS = {
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/webp': ['.webp'],
}

# Allowed font types for font uploads
ALLOWED_FONT_EXTENSIONS = {
    'font/ttf': ['.ttf'],
    'font/woff': ['.woff'],
    'font/woff2': ['.woff2'],
    'application/x-font-ttf': ['.ttf'],
    'application/font-woff': ['.woff'],
    'application/font-woff2': ['.woff2'],
    'application/octet-stream': ['.ttf', '.woff', '.woff2'],  # fallback for unknown mime types
}

# Maximum file size: 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024

# Maximum template image size: 20MB
MAX_TEMPLATE_IMAGE_SIZE = 20 * 1024 * 1024

# Maximum font file size: 10MB
MAX_FONT_FILE_SIZE = 10 * 1024 * 1024

# Upload directory
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/app/uploads"))


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

    def _validate_image_type(self, content_type: str, filename: str) -> bool:
        """Validate image type for template uploads."""
        if content_type not in ALLOWED_IMAGE_EXTENSIONS:
            return False
        
        ext = Path(filename).suffix.lower()
        return ext in ALLOWED_IMAGE_EXTENSIONS.get(content_type, [])

    def _get_image_dimensions(self, file_content: bytes) -> tuple[int, int]:
        """Get image dimensions from file content."""
        try:
            img = Image.open(BytesIO(file_content))
            return img.size  # (width, height)
        except Exception:
            raise ValueError("Could not read image dimensions. Invalid image file.")

    async def upload_template_image(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
    ) -> TemplateImageUploadResponse:
        """Upload a template image and return dimensions."""
        # Validate file size
        file_size = len(file_content)
        if file_size > MAX_TEMPLATE_IMAGE_SIZE:
            raise ValueError(
                f"فایل بزرگتر از حد مجاز است ({MAX_TEMPLATE_IMAGE_SIZE / 1024 / 1024}MB)"
            )
        
        # Validate file type
        if not self._validate_image_type(content_type, filename):
            raise ValueError(
                "فرمت فایل مجاز نیست. فرمت‌های مجاز: PNG, JPG, WEBP"
            )
        
        # Get image dimensions
        width, height = self._get_image_dimensions(file_content)
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(filename)
        
        # Create templates upload directory
        templates_dir = UPLOAD_DIR / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = templates_dir / unique_filename
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Generate URL
        file_url = f"/files/templates/{unique_filename}"
        
        log_event(
            event_type="template.image.uploaded",
            filename=unique_filename,
            original_filename=filename,
            file_size=file_size,
            content_type=content_type,
            width=width,
            height=height,
        )
        
        return TemplateImageUploadResponse(
            filename=filename,
            file_url=file_url,
            preview_url=file_url,
            file_size=file_size,
            content_type=content_type,
            width=width,
            height=height,
        )

    def _validate_font_type(self, content_type: str, filename: str) -> bool:
        """Validate font type for font uploads."""
        ext = Path(filename).suffix.lower()
        
        # Check by extension first (more reliable for fonts)
        valid_extensions = ['.ttf', '.woff', '.woff2']
        if ext in valid_extensions:
            return True
        
        # Fallback to content type check
        if content_type in ALLOWED_FONT_EXTENSIONS:
            return ext in ALLOWED_FONT_EXTENSIONS.get(content_type, [])
        
        return False

    async def upload_font_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
    ) -> dict:
        """Upload a font file and return its URL."""
        # Validate file size
        file_size = len(file_content)
        if file_size > MAX_FONT_FILE_SIZE:
            raise ValueError(
                f"فایل بزرگتر از حد مجاز است ({MAX_FONT_FILE_SIZE / 1024 / 1024}MB)"
            )
        
        # Validate file type
        if not self._validate_font_type(content_type, filename):
            raise ValueError(
                "فرمت فایل مجاز نیست. فرمت‌های مجاز: TTF, WOFF, WOFF2"
            )
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(filename)
        
        # Create fonts upload directory
        fonts_dir = UPLOAD_DIR / "fonts"
        fonts_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = fonts_dir / unique_filename
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Generate URL
        file_url = f"/files/fonts/{unique_filename}"
        
        log_event(
            event_type="font.file.uploaded",
            filename=unique_filename,
            original_filename=filename,
            file_size=file_size,
            content_type=content_type,
        )
        
        return {
            "filename": filename,
            "file_url": file_url,
            "file_size": file_size,
            "content_type": content_type,
        }










