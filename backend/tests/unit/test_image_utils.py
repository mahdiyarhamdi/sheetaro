"""Unit tests for image_utils thumbnail generation."""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image as PILImage


# Set up test environment before importing app code
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://sheetaro:sheetaro@localhost:5432/sheetaro_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DEBUG", "true")

# Use a temp directory for uploads during testing
TEST_UPLOAD_DIR = Path(tempfile.mkdtemp(prefix="sheetaro_test_thumb_"))
os.environ["UPLOAD_DIR"] = str(TEST_UPLOAD_DIR)

from app.utils.image_utils import generate_thumbnail, resolve_file_path


@pytest.fixture(autouse=True)
def clean_thumbs():
    """Clean thumbnails directory before each test."""
    thumbs = TEST_UPLOAD_DIR / "thumbs"
    if thumbs.exists():
        shutil.rmtree(thumbs)
    yield
    # Cleanup after test
    if thumbs.exists():
        shutil.rmtree(thumbs)


def _create_test_image(path: Path, width: int = 800, height: int = 600, fmt: str = "PNG") -> None:
    """Create a test image at the given path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = PILImage.new("RGB", (width, height), color="red")
    img.save(str(path), format=fmt)


class TestGenerateThumbnail:
    """Tests for generate_thumbnail()."""

    def test_generates_webp_thumbnail(self):
        """Thumbnail should be generated in WebP format."""
        src = TEST_UPLOAD_DIR / "templates" / "test.png"
        _create_test_image(src, 800, 600)

        result = generate_thumbnail(str(src), max_size=200)

        assert result is not None
        assert result.exists()
        assert result.suffix == ".webp"

    def test_thumbnail_is_smaller_than_max_size(self):
        """Thumbnail dimensions should not exceed max_size."""
        src = TEST_UPLOAD_DIR / "templates" / "big.png"
        _create_test_image(src, 2000, 1500)

        result = generate_thumbnail(str(src), max_size=300)
        assert result is not None

        with PILImage.open(result) as thumb:
            assert thumb.width <= 300
            assert thumb.height <= 300

    def test_uses_cache_on_second_call(self):
        """Second call should return the cached file without regenerating."""
        src = TEST_UPLOAD_DIR / "templates" / "cached.png"
        _create_test_image(src, 400, 300)

        result1 = generate_thumbnail(str(src), max_size=200)
        assert result1 is not None
        mtime1 = result1.stat().st_mtime

        result2 = generate_thumbnail(str(src), max_size=200)
        assert result2 is not None
        assert result2 == result1
        assert result2.stat().st_mtime == mtime1  # Same file, no regeneration

    def test_returns_none_for_missing_source(self):
        """Should return None if source file doesn't exist."""
        result = generate_thumbnail("/nonexistent/path/image.png", max_size=200)
        assert result is None

    def test_handles_rgba_image(self):
        """Should correctly convert RGBA images to RGB for WebP."""
        src = TEST_UPLOAD_DIR / "templates" / "rgba.png"
        src.parent.mkdir(parents=True, exist_ok=True)
        img = PILImage.new("RGBA", (400, 300), color=(255, 0, 0, 128))
        img.save(str(src), format="PNG")

        result = generate_thumbnail(str(src), max_size=200)
        assert result is not None
        assert result.exists()

    def test_different_max_sizes_produce_different_cache_files(self):
        """Different max_size values should create separate cache entries."""
        src = TEST_UPLOAD_DIR / "templates" / "multi.png"
        _create_test_image(src, 800, 600)

        result_200 = generate_thumbnail(str(src), max_size=200)
        result_400 = generate_thumbnail(str(src), max_size=400)

        assert result_200 is not None
        assert result_400 is not None
        assert result_200 != result_400

    def test_handles_jpeg_source(self):
        """Should work with JPEG source files."""
        src = TEST_UPLOAD_DIR / "templates" / "photo.jpg"
        _create_test_image(src, 1024, 768, fmt="JPEG")

        result = generate_thumbnail(str(src), max_size=300)
        assert result is not None
        assert result.suffix == ".webp"


class TestResolveFilePath:
    """Tests for resolve_file_path()."""

    def test_resolves_template_path(self):
        """Should resolve 'templates/filename' to UPLOAD_DIR/templates/filename."""
        test_file = TEST_UPLOAD_DIR / "templates" / "sample.png"
        _create_test_image(test_file, 100, 100)

        result = resolve_file_path("templates/sample.png")
        assert result is not None
        assert result == test_file

    def test_resolves_designs_path(self):
        """Should resolve 'designs/uid/filename' correctly."""
        uid = "test-user-123"
        test_file = TEST_UPLOAD_DIR / "designs" / uid / "file.png"
        _create_test_image(test_file, 100, 100)

        result = resolve_file_path(f"designs/{uid}/file.png")
        assert result is not None
        assert result == test_file

    def test_resolves_previews_to_root(self):
        """Previews should resolve from UPLOAD_DIR root."""
        test_file = TEST_UPLOAD_DIR / "dynamic_preview_abc.png"
        _create_test_image(test_file, 100, 100)

        result = resolve_file_path("previews/dynamic_preview_abc.png")
        assert result is not None
        assert result == test_file

    def test_returns_none_for_missing_file(self):
        """Should return None if the file doesn't exist."""
        result = resolve_file_path("templates/nonexistent.png")
        assert result is None

    def test_blocks_path_traversal(self):
        """Should block path traversal attempts."""
        result = resolve_file_path("../../etc/passwd")
        assert result is None

    def test_strips_leading_slash(self):
        """Should handle paths with leading slash."""
        test_file = TEST_UPLOAD_DIR / "templates" / "slash.png"
        _create_test_image(test_file, 100, 100)

        result = resolve_file_path("/templates/slash.png")
        assert result is not None

    def test_resolves_receipt_path(self):
        """Should resolve 'receipts/filename'."""
        test_file = TEST_UPLOAD_DIR / "receipts" / "receipt.png"
        _create_test_image(test_file, 100, 100)

        result = resolve_file_path("receipts/receipt.png")
        assert result is not None
        assert result == test_file
