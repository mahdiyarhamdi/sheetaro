"""Unit tests for FileService."""

import pytest
import pytest_asyncio
from pathlib import Path
from uuid import uuid4
import tempfile
import shutil

from app.services.file_service import FileService, MAX_FILE_SIZE, ALLOWED_EXTENSIONS


class TestFileService:
    """Test cases for FileService."""
    
    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create FileService instance with temp directory."""
        # Monkeypatch UPLOAD_DIR to use temp directory
        from app.services import file_service
        monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
        return FileService()
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Sample PDF file content (minimal PDF header)."""
        return b"%PDF-1.4\n%sample test pdf content"
    
    @pytest.fixture
    def sample_png_content(self):
        """Sample PNG file content (PNG header)."""
        return b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
    
    @pytest.fixture
    def user_id(self):
        """Generate test user ID."""
        return str(uuid4())
    
    @pytest.mark.asyncio
    async def test_upload_design_file_pdf(self, service, sample_pdf_content, user_id):
        """Test uploading a PDF file."""
        result = await service.upload_design_file(
            file_content=sample_pdf_content,
            filename="test_design.pdf",
            content_type="application/pdf",
            user_id=user_id,
        )
        
        assert result is not None
        assert result.filename == "test_design.pdf"
        assert result.file_url.startswith("/files/designs/")
        assert result.file_size == len(sample_pdf_content)
        assert result.content_type == "application/pdf"
    
    @pytest.mark.asyncio
    async def test_upload_design_file_png(self, service, sample_png_content, user_id):
        """Test uploading a PNG file."""
        result = await service.upload_design_file(
            file_content=sample_png_content,
            filename="logo.png",
            content_type="image/png",
            user_id=user_id,
        )
        
        assert result is not None
        assert result.content_type == "image/png"
    
    @pytest.mark.asyncio
    async def test_upload_file_too_large_fails(self, service, user_id):
        """Test that uploading oversized file fails."""
        # Create content larger than MAX_FILE_SIZE
        large_content = b"x" * (MAX_FILE_SIZE + 1)
        
        with pytest.raises(ValueError, match="File size exceeds maximum"):
            await service.upload_design_file(
                file_content=large_content,
                filename="large.pdf",
                content_type="application/pdf",
                user_id=user_id,
            )
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type_fails(self, service, user_id):
        """Test that uploading invalid file type fails."""
        with pytest.raises(ValueError, match="Invalid file type"):
            await service.upload_design_file(
                file_content=b"malicious content",
                filename="malware.exe",
                content_type="application/x-msdownload",
                user_id=user_id,
            )
    
    @pytest.mark.asyncio
    async def test_upload_mismatched_extension_fails(self, service, sample_pdf_content, user_id):
        """Test that uploading file with mismatched extension fails."""
        with pytest.raises(ValueError, match="Invalid file type"):
            await service.upload_design_file(
                file_content=sample_pdf_content,
                filename="test.jpg",  # Wrong extension for PDF content type
                content_type="application/pdf",
                user_id=user_id,
            )
    
    @pytest.mark.asyncio
    async def test_unique_filename_generation(self, service, sample_pdf_content, user_id):
        """Test that uploaded files get unique names."""
        result1 = await service.upload_design_file(
            file_content=sample_pdf_content,
            filename="design.pdf",
            content_type="application/pdf",
            user_id=user_id,
        )
        
        result2 = await service.upload_design_file(
            file_content=sample_pdf_content,
            filename="design.pdf",
            content_type="application/pdf",
            user_id=user_id,
        )
        
        # URLs should be different (unique filenames)
        assert result1.file_url != result2.file_url
    
    @pytest.mark.asyncio
    async def test_get_file_path(self, service, sample_pdf_content, user_id, tmp_path, monkeypatch):
        """Test getting actual file path from URL."""
        from app.services import file_service
        monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
        
        # Upload a file
        result = await service.upload_design_file(
            file_content=sample_pdf_content,
            filename="test.pdf",
            content_type="application/pdf",
            user_id=user_id,
        )
        
        # Get file path
        file_path = await service.get_file_path(result.file_url)
        
        assert file_path is not None
        assert file_path.exists()
    
    @pytest.mark.asyncio
    async def test_get_file_path_not_found(self, service):
        """Test getting file path for non-existent file."""
        result = await service.get_file_path("/files/designs/fake/nonexistent.pdf")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_file(self, service, sample_pdf_content, user_id, tmp_path, monkeypatch):
        """Test deleting a file."""
        from app.services import file_service
        monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
        
        # Upload a file
        result = await service.upload_design_file(
            file_content=sample_pdf_content,
            filename="to_delete.pdf",
            content_type="application/pdf",
            user_id=user_id,
        )
        
        # Verify it exists
        file_path = await service.get_file_path(result.file_url)
        assert file_path is not None
        assert file_path.exists()
        
        # Delete it
        success = await service.delete_file(result.file_url)
        
        assert success is True
        assert not file_path.exists()
    
    @pytest.mark.asyncio
    async def test_delete_file_not_found(self, service):
        """Test deleting non-existent file."""
        success = await service.delete_file("/files/designs/fake/nonexistent.pdf")
        
        assert success is False
    
    def test_validate_file_type_pdf(self, service):
        """Test file type validation for PDF."""
        assert service._validate_file_type("application/pdf", "test.pdf") is True
        assert service._validate_file_type("application/pdf", "test.PDF") is True  # Case insensitive
        assert service._validate_file_type("application/pdf", "test.jpg") is False
    
    def test_validate_file_type_images(self, service):
        """Test file type validation for images."""
        assert service._validate_file_type("image/png", "logo.png") is True
        assert service._validate_file_type("image/jpeg", "photo.jpg") is True
        assert service._validate_file_type("image/jpeg", "photo.jpeg") is True
        assert service._validate_file_type("image/svg+xml", "icon.svg") is True
    
    def test_validate_file_type_design_software(self, service):
        """Test file type validation for design software files."""
        assert service._validate_file_type("application/postscript", "design.ai") is True
        assert service._validate_file_type("application/postscript", "design.eps") is True
        assert service._validate_file_type("image/vnd.adobe.photoshop", "design.psd") is True
    
    def test_generate_unique_filename(self, service):
        """Test unique filename generation."""
        filename1 = service._generate_unique_filename("test.pdf")
        filename2 = service._generate_unique_filename("test.pdf")
        
        # Filenames should be different
        assert filename1 != filename2
        
        # Should preserve extension
        assert filename1.endswith(".pdf")
        assert filename2.endswith(".pdf")


class TestAllowedExtensions:
    """Test the ALLOWED_EXTENSIONS configuration."""
    
    def test_pdf_extensions(self):
        """Test PDF extensions are configured."""
        assert "application/pdf" in ALLOWED_EXTENSIONS
        assert ".pdf" in ALLOWED_EXTENSIONS["application/pdf"]
    
    def test_image_extensions(self):
        """Test image extensions are configured."""
        assert "image/png" in ALLOWED_EXTENSIONS
        assert "image/jpeg" in ALLOWED_EXTENSIONS
        assert "image/svg+xml" in ALLOWED_EXTENSIONS
    
    def test_max_file_size(self):
        """Test max file size is 100MB."""
        assert MAX_FILE_SIZE == 100 * 1024 * 1024

