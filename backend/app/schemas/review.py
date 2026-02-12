"""Schemas for order reviews and ratings."""

from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional review comment")
    review_type: Optional[str] = Field("PRINTSHOP", description="PRINTSHOP or DESIGNER")


class ReviewOut(BaseModel):
    """Schema for review output."""
    id: UUID
    order_id: UUID
    user_id: UUID
    printshop_id: Optional[UUID] = None
    designer_id: Optional[UUID] = None
    review_type: str = "PRINTSHOP"
    rating: int
    comment: Optional[str] = None
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    # Joined fields for display
    user_name: Optional[str] = None
    user_phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    """Schema for paginated review list."""
    items: List[ReviewOut]
    total: int
    page: int
    page_size: int
