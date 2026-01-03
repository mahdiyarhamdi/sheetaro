"""Service for template image processing - applying logo to templates."""

import os
import uuid
import httpx
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from app.models.design_template import DesignTemplate
from app.repositories.category_repository import CategoryRepository


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
                "preview_url": f"{base_url}/uploads/{preview_filename}",
                "final_url": f"{base_url}/uploads/{final_filename}",
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
                "preview_url": f"{base_url}/uploads/{preview_filename}",
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

