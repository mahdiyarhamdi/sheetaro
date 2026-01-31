"""Service for template image processing - applying logo to templates."""

import os
import uuid
import logging
import httpx
from io import BytesIO
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Libraries for Persian/Arabic text rendering
import arabic_reshaper
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)

from app.models.design_template import DesignTemplate, TemplatePlaceholder, PlaceholderType
from app.models.system_font import SystemFont
from app.repositories.category_repository import CategoryRepository


def reshape_persian_text(text: str) -> str:
    """Reshape Persian/Arabic text for correct rendering with Pillow.
    
    Persian/Arabic text requires:
    1. Reshaping: Characters change form based on position (initial, medial, final, isolated)
    2. BiDi: Right-to-left text direction
    """
    try:
        # Reshape the text (connect characters properly)
        reshaped = arabic_reshaper.reshape(text)
        # Apply bidirectional algorithm (RTL)
        bidi_text = get_display(reshaped)
        return bidi_text
    except Exception:
        # Fallback to original text if reshaping fails
        return text


class TemplateService:
    """Service for processing template images with logo placement."""
    
    def __init__(self, upload_dir: str = "/app/uploads", repository: Optional[CategoryRepository] = None):
        self.upload_dir = upload_dir
        self.repository = repository
        os.makedirs(upload_dir, exist_ok=True)
    
    async def download_image(self, url: str) -> Image.Image:
        """Download image from URL and return as PIL Image."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
    
    async def load_image(self, url_or_path: str, base_url: str = "") -> Image.Image:
        """Load image from local path or remote URL.
        
        Args:
            url_or_path: Either a local path (/files/...) or full URL (http://...)
            base_url: Base URL to prepend for relative paths
            
        Returns:
            PIL Image object
        """
        # Check if it's a local file path
        if url_or_path.startswith("/files/"):
            # Convert to local filesystem path
            local_path = os.path.join(self.upload_dir, url_or_path.lstrip("/files/"))
            if os.path.exists(local_path):
                return Image.open(local_path)
            else:
                raise FileNotFoundError(f"Local file not found: {local_path}")
        
        # Check if it's a full URL
        if url_or_path.startswith(("http://", "https://")):
            return await self.download_image(url_or_path)
        
        # Try prepending base_url for relative paths
        if base_url and not url_or_path.startswith(("http://", "https://")):
            full_url = f"{base_url}{url_or_path}"
            return await self.download_image(full_url)
        
        raise ValueError(f"Cannot load image from: {url_or_path}")
    
    def apply_logo_to_template(
        self,
        template_image: Image.Image,
        logo_image: Image.Image,
        placeholder_x: int,
        placeholder_y: int,
        placeholder_width: int,
        placeholder_height: int,
    ) -> Image.Image:
        """Apply logo to template at the specified placeholder position."""
        # Convert images to RGBA for transparency support
        template = template_image.convert("RGBA")
        logo = logo_image.convert("RGBA")
        
        # Resize logo to fit placeholder while maintaining aspect ratio
        logo_ratio = logo.width / logo.height
        placeholder_ratio = placeholder_width / placeholder_height
        
        if logo_ratio > placeholder_ratio:
            # Logo is wider - fit to width
            new_width = placeholder_width
            new_height = int(placeholder_width / logo_ratio)
        else:
            # Logo is taller - fit to height
            new_height = placeholder_height
            new_width = int(placeholder_height * logo_ratio)
        
        logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center logo within placeholder
        offset_x = placeholder_x + (placeholder_width - new_width) // 2
        offset_y = placeholder_y + (placeholder_height - new_height) // 2
        
        # Create a copy of template and paste logo
        result = template.copy()
        
        # Fill placeholder area with white first (to cover red square)
        white_fill = Image.new("RGBA", (placeholder_width, placeholder_height), (255, 255, 255, 255))
        result.paste(white_fill, (placeholder_x, placeholder_y))
        
        # Paste logo with transparency
        result.paste(logo, (offset_x, offset_y), logo)
        
        return result
    
    def save_image(self, image: Image.Image, filename: str) -> str:
        """Save image to disk and return the file path."""
        filepath = os.path.join(self.upload_dir, filename)
        
        # Convert to RGB if saving as JPEG
        if filename.lower().endswith(('.jpg', '.jpeg')):
            image = image.convert("RGB")
        
        image.save(filepath, quality=95)
        return filepath
    
    async def process_template_with_logo(
        self,
        template: DesignTemplate,
        logo_url: str,
        base_url: str = "",
    ) -> dict:
        """
        Process a template with a logo and return preview and final URLs.
        
        Args:
            template: The design template with placeholder info
            logo_url: URL of the logo image
            base_url: Base URL for serving files
            
        Returns:
            dict with preview_url and final_url
        """
        try:
            # Download template and logo images
            template_image = await self.download_image(template.file_url)
            logo_image = await self.download_image(logo_url)
            
            # Apply logo to template
            result_image = self.apply_logo_to_template(
                template_image=template_image,
                logo_image=logo_image,
                placeholder_x=template.placeholder_x,
                placeholder_y=template.placeholder_y,
                placeholder_width=template.placeholder_width,
                placeholder_height=template.placeholder_height,
            )
            
            # Generate unique filename
            unique_id = str(uuid.uuid4())[:8]
            preview_filename = f"preview_{unique_id}.png"
            final_filename = f"final_{unique_id}.png"
            
            # Save preview (smaller size for display)
            preview_image = result_image.copy()
            preview_image.thumbnail((800, 800), Image.Resampling.LANCZOS)
            preview_path = self.save_image(preview_image, preview_filename)
            
            # Save final (full size for printing)
            final_path = self.save_image(result_image, final_filename)
            
            # Return URLs
            return {
                "preview_url": f"{base_url}/api/v1/files/previews/{preview_filename}",
                "final_url": f"{base_url}/api/v1/files/previews/{final_filename}",
            }
            
        except Exception as e:
            raise ValueError(f"Error processing template: {str(e)}")
    
    def create_placeholder_preview(
        self,
        width: int,
        height: int,
        placeholder_x: int,
        placeholder_y: int,
        placeholder_width: int,
        placeholder_height: int,
    ) -> Image.Image:
        """
        Create a preview image showing the placeholder position.
        Useful for admin to visualize where the logo will be placed.
        """
        # Create white background
        image = Image.new("RGB", (width, height), (255, 255, 255))
        
        # Draw red placeholder rectangle
        draw = ImageDraw.Draw(image)
        
        # Red rectangle for placeholder
        draw.rectangle(
            [
                placeholder_x,
                placeholder_y,
                placeholder_x + placeholder_width,
                placeholder_y + placeholder_height,
            ],
            fill=(255, 0, 0),
            outline=(200, 0, 0),
            width=2,
        )
        
        # Add text label
        try:
            font = ImageFont.load_default()
            text = "Logo Placeholder"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = placeholder_x + (placeholder_width - text_width) // 2
            text_y = placeholder_y + (placeholder_height - text_height) // 2
            draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
        except Exception:
            pass  # Skip text if font not available
        
        return image
    
    def add_placeholder_to_image(
        self,
        image: Image.Image,
        placeholder_x: int,
        placeholder_y: int,
        placeholder_width: int,
        placeholder_height: int,
    ) -> Image.Image:
        """
        Add a red placeholder rectangle to an existing image.
        Used when admin uploads a template to show where logo will go.
        """
        result = image.copy().convert("RGBA")
        draw = ImageDraw.Draw(result)
        
        # Draw semi-transparent red rectangle
        overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [
                placeholder_x,
                placeholder_y,
                placeholder_x + placeholder_width,
                placeholder_y + placeholder_height,
            ],
            fill=(255, 0, 0, 180),  # Semi-transparent red
            outline=(200, 0, 0, 255),
            width=3,
        )
        
        # Add text
        try:
            font = ImageFont.load_default()
            text = "Logo"
            text_bbox = overlay_draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = placeholder_x + (placeholder_width - text_width) // 2
            text_y = placeholder_y + (placeholder_height - text_height) // 2
            overlay_draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        except Exception:
            pass
        
        result = Image.alpha_composite(result, overlay)
        return result
    
    def get_image_dimensions(self, image: Image.Image) -> Tuple[int, int]:
        """Get image dimensions."""
        return image.size
    
    async def download_and_get_dimensions(self, url: str) -> Tuple[int, int]:
        """Download image and return its dimensions."""
        image = await self.download_image(url)
        return self.get_image_dimensions(image)
    
    def calculate_center_position(
        self,
        image_width: int,
        image_height: int,
        placeholder_size: int = 200,
    ) -> Tuple[int, int, int, int]:
        """Calculate center position for placeholder."""
        x = (image_width - placeholder_size) // 2
        y = (image_height - placeholder_size) // 2
        return x, y, placeholder_size, placeholder_size
    
    def calculate_corner_position(
        self,
        image_width: int,
        image_height: int,
        corner: str = "center",  # center, top_left, top_right, bottom_left, bottom_right
        placeholder_size: int = 200,
        margin: int = 50,
    ) -> Tuple[int, int, int, int]:
        """Calculate corner position for placeholder."""
        if corner == "center":
            return self.calculate_center_position(image_width, image_height, placeholder_size)
        elif corner == "top_left":
            return margin, margin, placeholder_size, placeholder_size
        elif corner == "top_right":
            return image_width - placeholder_size - margin, margin, placeholder_size, placeholder_size
        elif corner == "bottom_left":
            return margin, image_height - placeholder_size - margin, placeholder_size, placeholder_size
        elif corner == "bottom_right":
            return (
                image_width - placeholder_size - margin,
                image_height - placeholder_size - margin,
                placeholder_size,
                placeholder_size,
            )
        else:
            return self.calculate_center_position(image_width, image_height, placeholder_size)
    
    async def create_template_preview(
        self,
        file_url: str,
        placeholder_x: int,
        placeholder_y: int,
        placeholder_width: int,
        placeholder_height: int,
        base_url: str = "",
    ) -> dict:
        """
        Create a preview of a template with the placeholder visible.
        
        Returns:
            dict with preview_url, image_width, image_height
        """
        try:
            # Download the original image
            image = await self.download_image(file_url)
            width, height = self.get_image_dimensions(image)
            
            # Add placeholder to image
            preview_image = self.add_placeholder_to_image(
                image,
                placeholder_x,
                placeholder_y,
                placeholder_width,
                placeholder_height,
            )
            
            # Save preview
            unique_id = str(uuid.uuid4())[:8]
            preview_filename = f"template_preview_{unique_id}.png"
            preview_path = self.save_image(preview_image, preview_filename)
            
            return {
                "preview_url": f"{base_url}/api/v1/files/previews/{preview_filename}",
                "image_width": width,
                "image_height": height,
            }
        except Exception as e:
            raise ValueError(f"Error creating template preview: {str(e)}")
    
    async def process_and_save_design(
        self,
        template: DesignTemplate,
        logo_url: str,
        order_id: Optional[str] = None,
        base_url: str = "",
    ) -> dict:
        """
        Process a template with logo and optionally save to database.
        
        Returns:
            dict with preview_url, final_url, and optionally design_id
        """
        result = await self.process_template_with_logo(template, logo_url, base_url)
        
        if self.repository and order_id:
            from uuid import UUID
            design = await self.repository.create_processed_design(
                order_id=UUID(order_id) if order_id else None,
                template_id=template.id,
                logo_url=logo_url,
                preview_url=result["preview_url"],
                final_url=result["final_url"],
            )
            result["design_id"] = str(design.id)
        
        return result
    
    # ============== Dynamic Placeholder Support ==============
    
    def apply_image_placeholder(
        self,
        base_image: Image.Image,
        image_url_or_path: str,
        placeholder: TemplatePlaceholder,
        downloaded_images: dict,
    ) -> Image.Image:
        """Apply an image to a placeholder on the base image."""
        # Get the image (from cache or download)
        if image_url_or_path in downloaded_images:
            img = downloaded_images[image_url_or_path].copy()
        else:
            # This should be a downloaded image
            return base_image
        
        # Convert to RGBA for transparency
        img = img.convert("RGBA")
        base = base_image.convert("RGBA")
        
        # Resize to fit placeholder while maintaining aspect ratio
        img_ratio = img.width / img.height
        placeholder_ratio = placeholder.width / placeholder.height
        
        if img_ratio > placeholder_ratio:
            new_width = placeholder.width
            new_height = int(placeholder.width / img_ratio)
        else:
            new_height = placeholder.height
            new_width = int(placeholder.height * img_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Apply rotation if needed
        if placeholder.rotation:
            img = img.rotate(-placeholder.rotation, expand=True, resample=Image.Resampling.BICUBIC)
        
        # Center within placeholder
        offset_x = placeholder.x + (placeholder.width - img.width) // 2
        offset_y = placeholder.y + (placeholder.height - img.height) // 2
        
        # Create result and paste
        result = base.copy()
        result.paste(img, (offset_x, offset_y), img)
        
        return result
    
    async def apply_text_placeholder(
        self,
        base_image: Image.Image,
        text: str,
        placeholder: TemplatePlaceholder,
        font_cache: dict,
    ) -> Image.Image:
        """Apply text to a placeholder on the base image."""
        result = base_image.copy().convert("RGBA")
        draw = ImageDraw.Draw(result)
        
        # Get font (use async version to load from database)
        font = await self._get_font_async(placeholder, font_cache)
        
        # Parse color (support hex with optional alpha)
        color = self._parse_color(placeholder.font_color or "#000000")
        
        # Reshape Persian/Arabic text for correct rendering
        display_text = reshape_persian_text(text)
        
        # Calculate text position based on alignment
        text_bbox = draw.textbbox((0, 0), display_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Horizontal alignment (text_align is now a string: 'left', 'center', 'right')
        if placeholder.text_align == "center":
            x = placeholder.x + (placeholder.width - text_width) // 2
        elif placeholder.text_align == "right":
            x = placeholder.x + placeholder.width - text_width
        else:  # left or default
            x = placeholder.x
        
        # Vertical center
        y = placeholder.y + (placeholder.height - text_height) // 2
        
        # Draw text with reshaped Persian text
        draw.text((x, y), display_text, fill=color, font=font)
        
        return result
    
    def _get_font(self, placeholder: TemplatePlaceholder, font_cache: dict) -> ImageFont.FreeTypeFont:
        """Get or load font for placeholder (sync version for compatibility)."""
        font_key = f"{placeholder.font_family}_{placeholder.font_size}_{placeholder.font_weight}"
        
        if font_key in font_cache:
            return font_cache[font_key]
        
        font_size = placeholder.font_size or 24
        font_weight = placeholder.font_weight or 400
        
        # Check for custom font files using the old path structure
        if placeholder.font_family:
            font_paths = [
                f"/app/fonts/{placeholder.font_family}.ttf",
                f"/app/fonts/{placeholder.font_family}.otf",
                f"/usr/share/fonts/truetype/{placeholder.font_family}.ttf",
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, font_size)
                        font_cache[font_key] = font
                        return font
                    except Exception:
                        pass
        
        # Fallback to bundled Persian fonts
        persian_font_paths = [
            "/app/fonts/Vazirmatn-Regular.ttf",
            "/app/fonts/Vazir.ttf",
            "/app/fonts/IRANSans.ttf",
        ]
        for path in persian_font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, font_size)
                    font_cache[font_key] = font
                    return font
                except Exception:
                    pass
        
        # Fallback to default font
        try:
            font = ImageFont.load_default(size=font_size)
        except TypeError:
            font = ImageFont.load_default()
        
        font_cache[font_key] = font
        return font
    
    async def _get_font_async(self, placeholder: TemplatePlaceholder, font_cache: dict) -> ImageFont.FreeTypeFont:
        """Get or load font for placeholder from database.
        
        Priority:
        1. Font specified in placeholder.font_family (from database)
        2. Any available Persian font from database with variants
        3. Any TTF file in uploads/fonts directory
        4. Default font (last resort)
        """
        font_key = f"{placeholder.font_family}_{placeholder.font_size}_{placeholder.font_weight}"
        
        if font_key in font_cache:
            logger.debug(f"Font cache hit: {font_key}")
            return font_cache[font_key]
        
        font_size = placeholder.font_size or 24
        font_weight = placeholder.font_weight or 400
        
        logger.info(f"Loading font for placeholder: family={placeholder.font_family}, size={font_size}, weight={font_weight}")
        
        # Strategy 1: Try specified font from database
        if self.repository and placeholder.font_family:
            logger.debug(f"Strategy 1: Trying font from database: {placeholder.font_family}")
            font = await self._try_load_font_from_db(
                placeholder.font_family, font_size, font_weight
            )
            if font:
                logger.info(f"Strategy 1 SUCCESS: Loaded font from database: {placeholder.font_family}")
                font_cache[font_key] = font
                return font
        
        # Strategy 2: If no font_family specified, find ANY font with variants
        if self.repository:
            logger.debug("Strategy 2: Searching for any Persian font in database")
            font = await self._find_any_persian_font(font_size, font_weight)
            if font:
                logger.info("Strategy 2 SUCCESS: Found Persian font from database")
                font_cache[font_key] = font
                return font
        
        # Strategy 3: Fallback to any TTF in uploads/fonts directory
        logger.debug("Strategy 3: Searching for TTF in uploads/fonts")
        font = self._find_ttf_in_uploads(font_size)
        if font:
            logger.info("Strategy 3 SUCCESS: Found font in uploads/fonts")
            font_cache[font_key] = font
            return font
        
        # Strategy 4: Bundled Persian fonts (if exist)
        logger.debug("Strategy 4: Checking bundled fonts")
        persian_font_paths = [
            "/app/fonts/Vazirmatn-Regular.ttf",
            "/app/fonts/Vazir.ttf",
            "/app/fonts/IRANSans.ttf",
        ]
        for path in persian_font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, font_size)
                    logger.info(f"Strategy 4 SUCCESS: Loaded bundled font: {path}")
                    font_cache[font_key] = font
                    return font
                except Exception as e:
                    logger.warning(f"Failed to load bundled font {path}: {e}")
        
        # Strategy 5: Last fallback to default font (won't render Persian correctly)
        logger.warning("Strategy 5: Using default font - Persian text may not render correctly!")
        try:
            font = ImageFont.load_default(size=font_size)
        except TypeError:
            font = ImageFont.load_default()
        
        font_cache[font_key] = font
        return font
    
    async def _try_load_font_from_db(
        self, font_name: str, font_size: int, font_weight: int
    ) -> Optional[ImageFont.FreeTypeFont]:
        """Try to load a specific font from database by name."""
        if not self.repository:
            return None
        
        # Try by name first, then by name_fa
        font_record = await self.repository.get_font_by_name(font_name)
        if not font_record:
            font_record = await self.repository.get_font_by_name_fa(font_name)
        
        if font_record and font_record.variants:
            return self._load_font_variant(font_record.variants, font_size, font_weight)
        
        return None
    
    async def _find_any_persian_font(
        self, font_size: int, font_weight: int
    ) -> Optional[ImageFont.FreeTypeFont]:
        """Find any available font with variants from database."""
        if not self.repository:
            return None
        
        # Get all fonts and find one with non-empty variants
        # Note: We fetch all fonts because JSON column comparison with != None 
        # doesn't work correctly for empty arrays
        from sqlalchemy import select
        from app.models.system_font import SystemFont
        
        result = await self.repository.db.execute(select(SystemFont))
        fonts = result.scalars().all()
        
        for font_record in fonts:
            # Check if variants is not None and has at least one entry
            if font_record.variants and len(font_record.variants) > 0:
                font = self._load_font_variant(font_record.variants, font_size, font_weight)
                if font:
                    return font
        
        return None
    
    def _load_font_variant(
        self, variants: list, font_size: int, font_weight: int, require_persian_support: bool = True
    ) -> Optional[ImageFont.FreeTypeFont]:
        """Load font from variant list, preferring matching weight.
        
        Args:
            variants: List of font variant dicts with weight, style, file_url
            font_size: Font size to load
            font_weight: Preferred font weight
            require_persian_support: If True, skip fonts that don't support Arabic Presentation Forms
        """
        best_variant = None
        
        for variant in variants:
            if variant.get("weight") == font_weight:
                best_variant = variant
                break
            if best_variant is None:
                best_variant = variant
        
        if best_variant:
            file_url = best_variant.get("file_url", "")
            local_path = self._get_font_local_path(file_url)
            
            if local_path and os.path.exists(local_path):
                try:
                    font = ImageFont.truetype(local_path, font_size)
                    
                    # Check if font supports Arabic Presentation Forms for Persian text
                    if require_persian_support and not self._font_supports_persian(local_path):
                        logger.warning(f"Font {local_path} does not support Persian text, skipping")
                        return None
                    
                    return font
                except Exception as e:
                    logger.warning(f"Failed to load font from {local_path}: {e}")
        
        return None
    
    def _font_supports_persian(self, font_path: str) -> bool:
        """Check if a font file supports Arabic Presentation Forms (required for Persian).
        
        Tests for the presence of specific Arabic Presentation Form characters
        that are used when text is reshaped with arabic_reshaper.
        """
        try:
            from fontTools.ttLib import TTFont
            tt = TTFont(font_path)
            cmap = tt.getBestCmap()
            
            # Arabic Presentation Forms-B characters (U+FE70-U+FEFF)
            # These are used by arabic_reshaper for connected letters
            test_chars = [
                0xFE91,  # ARABIC LETTER BEH INITIAL FORM
                0xFEA3,  # ARABIC LETTER HAH MEDIAL FORM
                0xFBFC,  # ARABIC LETTER FARSI YEH
            ]
            
            # Font should have at least 2 of these characters
            supported_count = sum(1 for char in test_chars if char in cmap)
            return supported_count >= 2
        except Exception as e:
            logger.debug(f"Could not check font Persian support: {e}")
            # If we can't check, assume it supports Persian (don't block)
            return True
    
    def _get_font_local_path(self, file_url: str) -> Optional[str]:
        """Convert font file URL to local path."""
        if not file_url:
            return None
        
        # Handle various URL prefixes
        if file_url.startswith("/api/v1/files/"):
            return os.path.join(self.upload_dir, file_url.replace("/api/v1/files/", ""))
        elif file_url.startswith("/files/"):
            return os.path.join(self.upload_dir, file_url.replace("/files/", ""))
        
        return None
    
    def _find_ttf_in_uploads(self, font_size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Find a TTF font in uploads/fonts directory.
        
        Priority: Vazirmatn (best Persian support) > any other TTF
        """
        fonts_dir = os.path.join(self.upload_dir, "fonts")
        logger.debug(f"Looking for fonts in: {fonts_dir}")
        
        if not os.path.exists(fonts_dir):
            logger.warning(f"Fonts directory does not exist: {fonts_dir}")
            return None
        
        # List available files for debugging
        available_files = os.listdir(fonts_dir)
        logger.debug(f"Available font files: {available_files}")
        
        # Priority list: fonts known to have good Arabic Presentation Forms support
        priority_fonts = [
            "Vazirmatn-Regular.ttf",
            "Vazirmatn-Bold.ttf",
            "Vazir-Regular.ttf",
            "IRANSans.ttf",
        ]
        
        # Try priority fonts first
        for priority_name in priority_fonts:
            font_path = os.path.join(fonts_dir, priority_name)
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    logger.info(f"Loaded priority font: {font_path}")
                    return font
                except Exception as e:
                    logger.warning(f"Failed to load priority font {font_path}: {e}")
                    continue
        
        # Fallback to any TTF
        for filename in available_files:
            if filename.endswith(".ttf"):
                font_path = os.path.join(fonts_dir, filename)
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    logger.info(f"Loaded fallback font: {font_path}")
                    return font
                except Exception as e:
                    logger.warning(f"Failed to load font {font_path}: {e}")
                    continue
        
        logger.warning("No TTF fonts found in uploads/fonts directory")
        return None
    
    def _parse_color(self, color_str: str) -> Tuple[int, int, int, int]:
        """Parse hex color to RGBA tuple."""
        color_str = color_str.lstrip("#")
        
        if len(color_str) == 6:
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return (r, g, b, 255)
        elif len(color_str) == 8:
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            a = int(color_str[6:8], 16)
            return (r, g, b, a)
        else:
            return (0, 0, 0, 255)
    
    async def generate_preview(
        self,
        template: DesignTemplate,
        placeholder_data: List[dict],
        base_url: str = "",
    ) -> dict:
        """
        Generate a preview of the template with placeholder data.
        
        Args:
            template: DesignTemplate with placeholders relationship loaded
            placeholder_data: List of dicts with placeholder_id and image_url/text_value
            base_url: Base URL for serving files
            
        Returns:
            dict with preview_url, width, height
        """
        try:
            # Load base template image (from local file or remote URL)
            if not template.file_url:
                raise ValueError("Template has no file_url")
            
            base_image = await self.load_image(template.file_url, base_url)
            width, height = self.get_image_dimensions(base_image)
            
            # Build placeholder data lookup
            placeholder_values = {str(d["placeholder_id"]): d for d in placeholder_data}
            
            # Load all images first (from local files or remote URLs)
            downloaded_images = {}
            for data in placeholder_data:
                if data.get("image_url"):
                    try:
                        downloaded_images[data["image_url"]] = await self.load_image(data["image_url"], base_url)
                    except Exception:
                        pass  # Skip failed loads
            
            # Font cache
            font_cache = {}
            
            # Process each placeholder
            result_image = base_image.copy().convert("RGBA")
            
            for placeholder in sorted(template.placeholders, key=lambda p: p.sort_order):
                if not placeholder.is_active:
                    continue
                
                placeholder_id = str(placeholder.id)
                if placeholder_id not in placeholder_values:
                    continue
                
                data = placeholder_values[placeholder_id]
                
                if placeholder.type == PlaceholderType.IMAGE:
                    if data.get("image_url"):
                        result_image = self.apply_image_placeholder(
                            result_image,
                            data["image_url"],
                            placeholder,
                            downloaded_images,
                        )
                elif placeholder.type == PlaceholderType.TEXT:
                    text = data.get("text_value") or placeholder.default_value or ""
                    if text:
                        result_image = await self.apply_text_placeholder(
                            result_image,
                            text,
                            placeholder,
                            font_cache,
                        )
            
            # Save preview
            unique_id = str(uuid.uuid4())[:8]
            preview_filename = f"dynamic_preview_{unique_id}.png"
            preview_path = self.save_image(result_image, preview_filename)
            
            return {
                "preview_url": f"{base_url}/api/v1/files/previews/{preview_filename}",
                "width": width,
                "height": height,
            }
            
        except Exception as e:
            raise ValueError(f"Error generating preview: {str(e)}")

