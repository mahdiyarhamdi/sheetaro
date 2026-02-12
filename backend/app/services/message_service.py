"""Message service for order-scoped chat (PRIVATE plan only)."""

from uuid import UUID
from typing import Optional

from sqlalchemy import select, func as sa_func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.models.order import Order
from app.models.user import User
from app.models.enums import OrderStatus, DesignPlan
from app.schemas.message import MessageOut, MessageListResponse
from app.repositories.order_repository import OrderRepository
from app.utils.logger import log_event


class MessageService:
    """Service for order chat messaging."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)

    async def send_message(
        self,
        order_id: UUID,
        sender_id: UUID,
        content: str,
        file_url: Optional[str] = None,
    ) -> MessageOut:
        """Send a chat message within an order context."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        # Chat only available for PRIVATE plans
        if order.design_plan != DesignPlan.PRIVATE:
            raise PermissionError("Chat is only available for PRIVATE design plans")

        # Chat only while DESIGNING
        if order.status != OrderStatus.DESIGNING:
            raise ValueError("Chat is only available while order is in DESIGNING status")

        # Only order owner or assigned designer can chat
        if sender_id != order.user_id and sender_id != order.assigned_designer_id:
            raise PermissionError("You do not have permission to send messages on this order")

        msg = Message(
            order_id=order_id,
            sender_id=sender_id,
            content=content,
            file_url=file_url,
        )
        self.db.add(msg)
        await self.db.flush()

        # Get sender name
        sender_name = await self._get_user_name(sender_id)

        log_event(
            event_type="message.sent",
            order_id=str(order_id),
            sender_id=str(sender_id),
        )

        out = MessageOut.model_validate(msg)
        out.sender_name = sender_name
        return out

    async def get_messages(
        self,
        order_id: UUID,
        user_id: UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> MessageListResponse:
        """Get paginated messages for an order."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        # Access control: only owner or assigned designer
        if user_id != order.user_id and user_id != order.assigned_designer_id:
            raise PermissionError("You do not have access to messages for this order")

        page_size = min(page_size, 100)
        page = max(page, 1)
        offset = (page - 1) * page_size

        # Count total
        count_result = await self.db.execute(
            select(sa_func.count(Message.id)).where(Message.order_id == order_id)
        )
        total = count_result.scalar() or 0

        # Fetch page
        result = await self.db.execute(
            select(Message)
            .where(Message.order_id == order_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(page_size)
        )
        messages = list(result.scalars().all())

        # Resolve sender names
        items = []
        for msg in messages:
            out = MessageOut.model_validate(msg)
            out.sender_name = await self._get_user_name(msg.sender_id)
            items.append(out)

        return MessageListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def mark_read(self, order_id: UUID, user_id: UUID) -> int:
        """Mark all messages as read for a user in an order. Returns count updated."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        if user_id != order.user_id and user_id != order.assigned_designer_id:
            raise PermissionError("You do not have access to messages for this order")

        # Mark messages from the OTHER participant as read
        result = await self.db.execute(
            update(Message)
            .where(
                Message.order_id == order_id,
                Message.sender_id != user_id,
                Message.is_read == False,  # noqa: E712
            )
            .values(is_read=True)
        )
        await self.db.flush()
        return result.rowcount

    async def get_unread_count(self, order_id: UUID, user_id: UUID) -> int:
        """Count unread messages for a user in an order."""
        result = await self.db.execute(
            select(sa_func.count(Message.id)).where(
                Message.order_id == order_id,
                Message.sender_id != user_id,
                Message.is_read == False,  # noqa: E712
            )
        )
        return result.scalar() or 0

    # ── Private helpers ──────────────────────────────────────

    async def _get_user_name(self, user_id: UUID) -> Optional[str]:
        """Fetch display name for a user."""
        result = await self.db.execute(
            select(User.first_name, User.last_name).where(User.id == user_id)
        )
        row = result.first()
        if row:
            return f"{row.first_name} {row.last_name or ''}".strip()
        return None
