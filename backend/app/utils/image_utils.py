"""Image utilities for thumbnail generation and optimization."""

import hashlib
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)


def _get_upload_dir() -> Path:
    """Get the current UPLOAD_DIR (supports runtime override via env var)."""
    return Path(os.environ.get("UPLOAD_DIR", "/app/uploads"))


def _get_thumbs_dir() -> Path:
    """Get the thumbnails cache directory."""
    return _get_upload_dir() / "thumbs"


def _ensure_thumbs_dir() -> None:
    """Create thumbnails cache directory if it doesn't exist."""
    _get_thumbs_dir().mkdir(parents=True, exist_ok=True)


def _thumb_cache_key(source_path: str, max_size: int) -> str:
    """Generate a deterministic cache key for a thumbnail."""
    digest = hashlib.md5(source_path.encode()).hexdigest()[:12]
    return f"{digest}_{max_size}.webp"


def get_cached_thumbnail(source_path: str, max_size: int = 400) -> Optional[Path]:
    """Return the cached thumbnail path if it exists."""
    _ensure_thumbs_dir()
    cache_file = _get_thumbs_dir() / _thumb_cache_key(source_path, max_size)
    if cache_file.exists():
        return cache_file
    return None


def generate_thumbnail(
    source_path: str,
    max_size: int = 400,
) -> Optional[Path]:
    """Generate an optimized WebP thumbnail and cache it to disk.

    Args:
        source_path: Absolute path to the original image file.
        max_size: Maximum dimension (width or height) of the thumbnail.

    Returns:
        Path to the generated thumbnail, or None on failure.
    """
    _ensure_thumbs_dir()

    cache_key = _thumb_cache_key(source_path, max_size)
    cache_file = _get_thumbs_dir() / cache_key

    # Return cached version if available
    if cache_file.exists():
        return cache_file

    src = Path(source_path)
    if not src.exists():
        logger.warning("Thumbnail source not found: %s", source_path)
        return None

    try:
        with Image.open(src) as img:
            # Convert RGBA to RGB for WebP compatibility (if needed)
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                img = background

            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            img.save(str(cache_file), format="WEBP", quality=80)
            logger.info("Generated thumbnail: %s (%dx%d)", cache_key, img.width, img.height)
            return cache_file
    except Exception:
        logger.exception("Failed to generate thumbnail for %s", source_path)
        return None


def resolve_file_path(relative_path: str) -> Optional[Path]:
    """Resolve a relative file path (like 'templates/abc.png' or 'dynamic_preview_x.png')
    to an absolute path within UPLOAD_DIR.

    Handles:
        - 'templates/filename'    -> UPLOAD_DIR / templates / filename
        - 'designs/uid/filename'  -> UPLOAD_DIR / designs / uid / filename
        - 'receipts/filename'     -> UPLOAD_DIR / receipts / filename
        - 'previews/filename'     -> UPLOAD_DIR / filename  (previews are stored at root)
        - 'filename'              -> UPLOAD_DIR / filename
    """
    # Security: prevent path traversal
    clean = relative_path.replace("\\", "/").lstrip("/")
    if ".." in clean:
        return None

    upload_dir = _get_upload_dir()

    # Previews are stored at UPLOAD_DIR root level
    if clean.startswith("previews/"):
        filename = clean[len("previews/"):]
        candidate = upload_dir / filename
    else:
        candidate = upload_dir / clean

    if candidate.exists() and candidate.is_file():
        return candidate
    return None
