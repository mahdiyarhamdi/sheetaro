"""Integration tests for thumbnail and download file endpoints."""

import os
import tempfile
import shutil
from pathlib import Path

import pytest
import pytest_asyncio
from PIL import Image as PILImage

# Set up test environment before any app imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://sheetaro:sheetaro@localhost:5432/sheetaro_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DEBUG", "true")

TEST_UPLOAD_DIR = Path(tempfile.mkdtemp(prefix="sheetaro_thumb_api_"))
os.environ["UPLOAD_DIR"] = str(TEST_UPLOAD_DIR)

from httpx import AsyncClient, ASGITransport
from app.main import app


def _create_test_image(path: Path, width: int = 800, height: int = 600, fmt: str = "PNG") -> None:
    """Create a test image at the given path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = PILImage.new("RGB", (width, height), color="blue")
    img.save(str(path), format=fmt)


@pytest_asyncio.fixture
async def client():
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def setup_files():
    """Set up test files and clean up."""
    # Create test images
    _create_test_image(TEST_UPLOAD_DIR / "templates" / "test_template.png", 1000, 800)
    _create_test_image(TEST_UPLOAD_DIR / "receipts" / "test_receipt.jpg", 500, 400, fmt="JPEG")
    _create_test_image(TEST_UPLOAD_DIR / "dynamic_preview_test123.png", 600, 400)
    _create_test_image(TEST_UPLOAD_DIR / "designs" / "user-1" / "design.png", 2000, 1500)

    # Clean thumbs
    thumbs = TEST_UPLOAD_DIR / "thumbs"
    if thumbs.exists():
        shutil.rmtree(thumbs)

    yield

    if thumbs.exists():
        shutil.rmtree(thumbs)


@pytest.mark.asyncio
class TestThumbnailEndpoint:
    """Tests for GET /api/v1/files/thumbnail/{path}."""

    async def test_returns_webp_thumbnail(self, client: AsyncClient):
        """Should return a WebP thumbnail."""
        resp = await client.get("/api/v1/files/thumbnail/templates/test_template.png")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/webp"

    async def test_thumbnail_respects_max_size(self, client: AsyncClient):
        """Should respect the max_size query parameter."""
        resp = await client.get("/api/v1/files/thumbnail/templates/test_template.png?max_size=100")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/webp"

    async def test_returns_404_for_missing_file(self, client: AsyncClient):
        """Should return 404 if the source file doesn't exist."""
        resp = await client.get("/api/v1/files/thumbnail/templates/nonexistent.png")
        assert resp.status_code == 404

    async def test_thumbnail_for_design_file(self, client: AsyncClient):
        """Should work with design file paths."""
        resp = await client.get("/api/v1/files/thumbnail/designs/user-1/design.png")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/webp"

    async def test_thumbnail_for_preview_file(self, client: AsyncClient):
        """Should work with preview file paths (stored at root)."""
        resp = await client.get("/api/v1/files/thumbnail/previews/dynamic_preview_test123.png")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/webp"

    async def test_thumbnail_for_receipt(self, client: AsyncClient):
        """Should work with receipt file paths."""
        resp = await client.get("/api/v1/files/thumbnail/receipts/test_receipt.jpg")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/webp"

    async def test_max_size_validation(self, client: AsyncClient):
        """Should validate max_size parameter bounds."""
        # Too small
        resp = await client.get("/api/v1/files/thumbnail/templates/test_template.png?max_size=10")
        assert resp.status_code == 422

        # Too large
        resp = await client.get("/api/v1/files/thumbnail/templates/test_template.png?max_size=2000")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestDownloadEndpoint:
    """Tests for GET /api/v1/files/download/{path}."""

    async def test_returns_original_file_with_attachment_header(self, client: AsyncClient):
        """Should return original file with Content-Disposition: attachment."""
        resp = await client.get("/api/v1/files/download/templates/test_template.png")
        assert resp.status_code == 200
        assert "attachment" in resp.headers.get("content-disposition", "")
        assert resp.headers["content-type"] == "image/png"

    async def test_download_jpeg(self, client: AsyncClient):
        """Should serve JPEG with correct content type."""
        resp = await client.get("/api/v1/files/download/receipts/test_receipt.jpg")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/jpeg"
        assert "attachment" in resp.headers.get("content-disposition", "")

    async def test_returns_404_for_missing_file(self, client: AsyncClient):
        """Should return 404 for nonexistent files."""
        resp = await client.get("/api/v1/files/download/templates/nonexistent.png")
        assert resp.status_code == 404

    async def test_download_design_file(self, client: AsyncClient):
        """Should serve design files."""
        resp = await client.get("/api/v1/files/download/designs/user-1/design.png")
        assert resp.status_code == 200
        assert "attachment" in resp.headers.get("content-disposition", "")

    async def test_download_preview_file(self, client: AsyncClient):
        """Should serve preview files from root."""
        resp = await client.get("/api/v1/files/download/previews/dynamic_preview_test123.png")
        assert resp.status_code == 200
        assert "attachment" in resp.headers.get("content-disposition", "")
