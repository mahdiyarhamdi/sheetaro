"""API endpoints for system font management."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_admin_user
from app.models.system_font import SystemFont
from app.schemas.category import (
    SystemFontCreate, SystemFontUpdate, SystemFontOut,
)

router = APIRouter(prefix="/api/v1/fonts", tags=["fonts"])


# ============== Font Endpoints ==============

@router.get("", response_model=List[SystemFontOut])
async def list_fonts(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all system fonts."""
    query = select(SystemFont)
    if active_only:
        query = query.where(SystemFont.is_active == True)
    query = query.order_by(SystemFont.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{font_id}", response_model=SystemFontOut)
async def get_font(
    font_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a font by ID."""
    result = await db.execute(
        select(SystemFont).where(SystemFont.id == font_id)
    )
    font = result.scalar_one_or_none()
    if not font:
        raise HTTPException(status_code=404, detail="Font not found")
    return font


@router.post("", response_model=SystemFontOut, status_code=status.HTTP_201_CREATED)
async def create_font(
    data: SystemFontCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new font. Admin only."""
    # Check for duplicate name
    existing = await db.execute(
        select(SystemFont).where(SystemFont.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Font with this name already exists")
    
    font = SystemFont(
        name=data.name,
        name_fa=data.name_fa,
        file_url=data.file_url,
        variants=[v.model_dump() for v in data.variants] if data.variants else [],
        sample_text=data.sample_text,
    )
    db.add(font)
    await db.commit()
    await db.refresh(font)
    return font


@router.patch("/{font_id}", response_model=SystemFontOut)
async def update_font(
    font_id: UUID,
    data: SystemFontUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update a font. Admin only."""
    result = await db.execute(
        select(SystemFont).where(SystemFont.id == font_id)
    )
    font = result.scalar_one_or_none()
    if not font:
        raise HTTPException(status_code=404, detail="Font not found")
    
    # Check for duplicate name if changing
    if data.name and data.name != font.name:
        existing = await db.execute(
            select(SystemFont).where(SystemFont.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Font with this name already exists")
    
    update_data = data.model_dump(exclude_unset=True)
    if 'variants' in update_data and update_data['variants']:
        update_data['variants'] = [v.model_dump() if hasattr(v, 'model_dump') else v for v in update_data['variants']]
    
    for key, value in update_data.items():
        setattr(font, key, value)
    
    await db.commit()
    await db.refresh(font)
    return font


@router.delete("/{font_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_font(
    font_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a font. Admin only."""
    result = await db.execute(
        select(SystemFont).where(SystemFont.id == font_id)
    )
    font = result.scalar_one_or_none()
    if not font:
        raise HTTPException(status_code=404, detail="Font not found")
    
    await db.delete(font)
    await db.commit()


@router.post("/{font_id}/variants", response_model=SystemFontOut)
async def add_font_variant(
    font_id: UUID,
    weight: int,
    style: str = "normal",
    file_url: str = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Add a variant to a font. Admin only."""
    result = await db.execute(
        select(SystemFont).where(SystemFont.id == font_id)
    )
    font = result.scalar_one_or_none()
    if not font:
        raise HTTPException(status_code=404, detail="Font not found")
    
    # Add new variant
    variants = list(font.variants or [])
    new_variant = {"weight": weight, "style": style, "file_url": file_url}
    
    # Replace if same weight/style exists
    variants = [v for v in variants if not (v.get("weight") == weight and v.get("style") == style)]
    variants.append(new_variant)
    font.variants = variants
    
    await db.commit()
    await db.refresh(font)
    return font


@router.delete("/{font_id}/variants/{weight}")
async def delete_font_variant(
    font_id: UUID,
    weight: int,
    style: str = "normal",
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a variant from a font. Admin only."""
    result = await db.execute(
        select(SystemFont).where(SystemFont.id == font_id)
    )
    font = result.scalar_one_or_none()
    if not font:
        raise HTTPException(status_code=404, detail="Font not found")
    
    # Remove variant
    variants = [v for v in (font.variants or []) if not (v.get("weight") == weight and v.get("style") == style)]
    font.variants = variants
    
    await db.commit()
    await db.refresh(font)
    return font

