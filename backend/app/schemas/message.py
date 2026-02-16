"""Message schemas for order chat."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class MessageCreate(BaseModel):
    """Schema for creating a message (text, file, or both)."""
    content: str = Field("", max_length=5000, description="Message text (optional if file_url provided)")
    file_url: Optional[str] = Field(None, max_length=500, description="Attached file URL")

    def model_post_init(self, __context: object) -> None:
        """Validate that at least content or file_url is provided."""
        if not self.content.strip() and not self.file_url:
            raise ValueError("Either content or file_url must be provided")


class MessageOut(BaseModel):
    """Output schema for a message."""
    id: UUID
    order_id: UUID
    sender_id: UUID
    sender_name: Optional[str] = None
    content: str = ""
    file_url: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """Paginated response for messages."""
    items: List[MessageOut]
    total: int
    page: int
    page_size: int
