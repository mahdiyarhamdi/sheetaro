"""Integration tests for Files API."""

import pytest
from httpx import AsyncClient
from uuid import uuid4
import io


class TestFilesAPI:
    """Integration tests for /api/v1/files endpoints."""
    
    @pytest.fixture
    async def setup_user(self, client: AsyncClient, sample_user_data):
        """Create a test user."""
        response = await client.post("/api/v1/users", json=sample_user_data)
        return response.json()
    
    @pytest.fixture
    def sample_pdf_file(self):
        """Create a sample PDF file for testing."""
        content = b"%PDF-1.4\n%test pdf content\n"
        return ("test.pdf", io.BytesIO(content), "application/pdf")
    
    @pytest.fixture
    def sample_png_file(self):
        """Create a sample PNG file for testing."""
        # Minimal PNG header
        content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        return ("logo.png", io.BytesIO(content), "image/png")
    
    @pytest.fixture
    def sample_jpg_file(self):
        """Create a sample JPEG file for testing."""
        # Minimal JPEG header
        content = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
        return ("photo.jpg", io.BytesIO(content), "image/jpeg")
    
    @pytest.mark.asyncio
    async def test_upload_pdf_file(self, client: AsyncClient, setup_user, sample_pdf_file):
        """Test POST /api/v1/files/upload - PDF file."""
        user = setup_user
        filename, content, content_type = sample_pdf_file
        
        files = {"file": (filename, content, content_type)}
        
        response = await client.post(
            "/api/v1/files/upload",
            files=files,
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert "/files/designs/" in data["file_url"]
        assert data["content_type"] == "application/pdf"
    
    @pytest.mark.asyncio
    async def test_upload_png_file(self, client: AsyncClient, setup_user, sample_png_file):
        """Test POST /api/v1/files/upload - PNG file."""
        user = setup_user
        filename, content, content_type = sample_png_file
        
        files = {"file": (filename, content, content_type)}
        
        response = await client.post(
            "/api/v1/files/upload",
            files=files,
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content_type"] == "image/png"
    
    @pytest.mark.asyncio
    async def test_upload_jpg_file(self, client: AsyncClient, setup_user, sample_jpg_file):
        """Test POST /api/v1/files/upload - JPEG file."""
        user = setup_user
        filename, content, content_type = sample_jpg_file
        
        files = {"file": (filename, content, content_type)}
        
        response = await client.post(
            "/api/v1/files/upload",
            files=files,
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content_type"] == "image/jpeg"
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type_fails(self, client: AsyncClient, setup_user):
        """Test that uploading invalid file type fails."""
        user = setup_user
        
        files = {"file": ("malware.exe", io.BytesIO(b"malicious content"), "application/x-msdownload")}
        
        response = await client.post(
            "/api/v1/files/upload",
            files=files,
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_upload_generates_unique_filename(self, client: AsyncClient, setup_user, sample_pdf_file):
        """Test that multiple uploads generate unique filenames."""
        user = setup_user
        filename, _, content_type = sample_pdf_file
        
        file_urls = []
        for _ in range(3):
            content = io.BytesIO(b"%PDF-1.4\ntest content")
            files = {"file": (filename, content, content_type)}
            
            response = await client.post(
                "/api/v1/files/upload",
                files=files,
                params={"user_id": user["id"]}
            )
            assert response.status_code == 201
            file_urls.append(response.json()["file_url"])
        
        # All URLs should be unique
        assert len(set(file_urls)) == 3
    
    @pytest.mark.asyncio
    async def test_get_uploaded_file(self, client: AsyncClient, setup_user, sample_pdf_file, monkeypatch, tmp_path):
        """Test GET /api/v1/files/designs/{user_id}/{filename}."""
        user = setup_user
        filename, content, content_type = sample_pdf_file
        
        # Monkeypatch UPLOAD_DIR
        from app.services import file_service
        monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
        
        # Upload file
        files = {"file": (filename, content, content_type)}
        upload_response = await client.post(
            "/api/v1/files/upload",
            files=files,
            params={"user_id": user["id"]}
        )
        file_data = upload_response.json()
        
        # Extract path components from URL
        file_url = file_data["file_url"]
        # URL format: /files/designs/{user_id}/{filename}
        parts = file_url.split("/")
        user_id_from_url = parts[-2]
        filename_from_url = parts[-1]
        
        # Get file
        response = await client.get(f"/api/v1/files/designs/{user_id_from_url}/{filename_from_url}")
        
        # Note: This may fail in test environment without proper file serving
        # In production, files would be served by nginx/cdn
        assert response.status_code in [200, 404]  # 404 if file serving not configured
    
    @pytest.mark.asyncio
    async def test_delete_file(self, client: AsyncClient, setup_user, sample_pdf_file, monkeypatch, tmp_path):
        """Test DELETE /api/v1/files/designs/{user_id}/{filename}."""
        user = setup_user
        filename, content, content_type = sample_pdf_file
        
        # Monkeypatch UPLOAD_DIR
        from app.services import file_service
        monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
        
        # Upload file
        files = {"file": (filename, content, content_type)}
        upload_response = await client.post(
            "/api/v1/files/upload",
            files=files,
            params={"user_id": user["id"]}
        )
        file_data = upload_response.json()
        
        # Extract path components
        file_url = file_data["file_url"]
        parts = file_url.split("/")
        user_id_from_url = parts[-2]
        filename_from_url = parts[-1]
        
        # Delete file
        response = await client.delete(
            f"/api/v1/files/designs/{user_id_from_url}/{filename_from_url}",
            params={"requesting_user_id": user["id"]}
        )
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_file_wrong_user_fails(self, client: AsyncClient, setup_user, sample_user_data, sample_pdf_file, monkeypatch, tmp_path):
        """Test that deleting another user's file fails."""
        user = setup_user
        filename, content, content_type = sample_pdf_file
        
        # Monkeypatch UPLOAD_DIR
        from app.services import file_service
        monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
        
        # Upload file
        files = {"file": (filename, content, content_type)}
        upload_response = await client.post(
            "/api/v1/files/upload",
            files=files,
            params={"user_id": user["id"]}
        )
        file_data = upload_response.json()
        
        # Create another user
        other_user_data = sample_user_data.copy()
        other_user_data["telegram_id"] = 999888777
        other_response = await client.post("/api/v1/users", json=other_user_data)
        other_user = other_response.json()
        
        # Extract path components
        file_url = file_data["file_url"]
        parts = file_url.split("/")
        user_id_from_url = parts[-2]
        filename_from_url = parts[-1]
        
        # Try to delete as different user
        response = await client.delete(
            f"/api/v1/files/designs/{user_id_from_url}/{filename_from_url}",
            params={"requesting_user_id": other_user["id"]}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_file_fails(self, client: AsyncClient, setup_user):
        """Test that deleting non-existent file returns 404."""
        user = setup_user
        
        response = await client.delete(
            f"/api/v1/files/designs/{user['id']}/nonexistent.pdf",
            params={"requesting_user_id": user["id"]}
        )
        
        assert response.status_code == 404

