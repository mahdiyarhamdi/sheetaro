"""Design revision schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from app.models.enums import RevisionStatus


class DesignRevisionOut(BaseModel):
    """Output schema for a design revision."""
    id: UUID
    order_id: UUID
    version: int
    designer_id: UUID
    design_file_url: str
    customer_feedback: Optional[str] = None
    status: RevisionStatus
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DesignRevisionListResponse(BaseModel):
    """Response schema for revision list."""
    items: List[DesignRevisionOut]
    total: int


class RejectDesignRequest(BaseModel):
    """Request body for rejecting a design."""
    feedback: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Customer feedback explaining why the design was rejected",
    )
