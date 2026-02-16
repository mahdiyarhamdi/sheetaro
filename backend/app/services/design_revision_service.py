"""Design revision service for managing designer uploads and customer approvals."""

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, func as sa_func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.design_revision import DesignRevision
from app.models.order import Order
from app.models.enums import RevisionStatus, OrderStatus
from app.schemas.design_revision import DesignRevisionOut, DesignRevisionListResponse
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.utils.logger import log_event
from app.utils.telegram_notify import (
    notify_customer_new_design_revision as tg_notify_customer_revision,
    notify_designer_design_approved as tg_notify_designer_approved,
    notify_designer_design_rejected as tg_notify_designer_rejected,
    notify_printshops_new_order as tg_notify_printshops,
    notify_admins_new_validation as tg_notify_admins_validation,
)

import logging as _logging
_logger = _logging.getLogger(__name__)


class DesignRevisionService:
    """Service for design revision workflow."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)

    async def submit_revision(
        self, order_id: UUID, designer_id: UUID, design_file_url: str
    ) -> DesignRevisionOut:
        """Designer uploads a new design revision for an order."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.status != OrderStatus.DESIGNING:
            raise ValueError("Order is not in DESIGNING status")
        if order.assigned_designer_id != designer_id:
            raise ValueError("You are not the assigned designer for this order")

        # Determine next version number
        result = await self.db.execute(
            select(sa_func.coalesce(sa_func.max(DesignRevision.version), 0))
            .where(DesignRevision.order_id == order_id)
        )
        current_max = result.scalar() or 0
        next_version = current_max + 1

        revision = DesignRevision(
            order_id=order_id,
            version=next_version,
            designer_id=designer_id,
            design_file_url=design_file_url,
            status=RevisionStatus.PENDING_REVIEW,
        )
        self.db.add(revision)

        # Update order's design_file_url to the latest
        order.design_file_url = design_file_url
        await self.db.flush()

        log_event(
            event_type="design.revision_submitted",
            order_id=str(order_id),
            designer_id=str(designer_id),
            version=next_version,
        )

        # Notify customer about the new revision
        try:
            if order.user and order.user.telegram_id:
                await tg_notify_customer_revision(order.user.telegram_id, str(order_id))
        except Exception as e:
            _logger.error(f"Notification error after revision submit: {e}")

        return DesignRevisionOut.model_validate(revision)

    async def approve_design(self, order_id: UUID, customer_id: UUID) -> DesignRevisionOut:
        """Customer approves the latest design revision."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.user_id != customer_id:
            raise ValueError("Only the order owner can approve designs")
        if order.status != OrderStatus.DESIGNING:
            raise ValueError("Order is not in DESIGNING status")

        latest = await self._get_latest_revision(order_id)
        if not latest:
            raise ValueError("No design revision found to approve")
        if latest.status != RevisionStatus.PENDING_REVIEW:
            raise ValueError("Latest revision is not pending review")

        # Mark revision as approved
        latest.status = RevisionStatus.APPROVED
        latest.reviewed_at = datetime.now(timezone.utc)

        # Transition order to next status
        await self._transition_after_approval(order)

        await self.db.flush()

        log_event(
            event_type="design.approved",
            order_id=str(order_id),
            customer_id=str(customer_id),
            version=latest.version,
        )

        # Notify designer and downstream roles
        try:
            await self._notify_after_approval(order)
        except Exception as e:
            _logger.error(f"Notification error after design approval: {e}")

        return DesignRevisionOut.model_validate(latest)

    async def reject_design(
        self, order_id: UUID, customer_id: UUID, feedback: str
    ) -> DesignRevisionOut:
        """Customer rejects the design with feedback. May auto-approve if max revisions reached."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.user_id != customer_id:
            raise ValueError("Only the order owner can reject designs")
        if order.status != OrderStatus.DESIGNING:
            raise ValueError("Order is not in DESIGNING status")

        latest = await self._get_latest_revision(order_id)
        if not latest:
            raise ValueError("No design revision found to reject")
        if latest.status != RevisionStatus.PENDING_REVIEW:
            raise ValueError("Latest revision is not pending review")

        # Mark revision as rejected with feedback
        latest.status = RevisionStatus.REJECTED
        latest.customer_feedback = feedback
        latest.reviewed_at = datetime.now(timezone.utc)

        # Increment revision count
        order.revision_count = (order.revision_count or 0) + 1

        # Check if max revisions reached -> auto-approve
        if order.max_revisions is not None and order.revision_count >= order.max_revisions:
            # Auto-approve: mark this revision as approved instead
            latest.status = RevisionStatus.APPROVED
            await self._transition_after_approval(order)

            log_event(
                event_type="design.auto_approved",
                order_id=str(order_id),
                reason="max_revisions_reached",
                revision_count=order.revision_count,
                max_revisions=order.max_revisions,
            )
        else:
            log_event(
                event_type="design.rejected",
                order_id=str(order_id),
                customer_id=str(customer_id),
                version=latest.version,
                revision_count=order.revision_count,
            )

            # Notify designer about rejection
            try:
                from app.models.user import User
                if order.assigned_designer_id:
                    designer = await self.db.get(User, order.assigned_designer_id)
                    if designer and designer.telegram_id:
                        await tg_notify_designer_rejected(designer.telegram_id, str(order_id), feedback)
            except Exception as e:
                _logger.error(f"Notification error after design rejection: {e}")

        await self.db.flush()
        return DesignRevisionOut.model_validate(latest)

    async def get_revision_history(self, order_id: UUID) -> DesignRevisionListResponse:
        """Get all revisions for an order, ordered by version."""
        result = await self.db.execute(
            select(DesignRevision)
            .where(DesignRevision.order_id == order_id)
            .order_by(DesignRevision.version.asc())
        )
        revisions = list(result.scalars().all())
        return DesignRevisionListResponse(
            items=[DesignRevisionOut.model_validate(r) for r in revisions],
            total=len(revisions),
        )

    async def get_latest_revision(self, order_id: UUID) -> Optional[DesignRevisionOut]:
        """Get the latest revision for an order."""
        rev = await self._get_latest_revision(order_id)
        if rev:
            return DesignRevisionOut.model_validate(rev)
        return None

    # ── Private helpers ──────────────────────────────────────

    async def _get_latest_revision(self, order_id: UUID) -> Optional[DesignRevision]:
        """Internal: fetch latest revision ORM object."""
        result = await self.db.execute(
            select(DesignRevision)
            .where(DesignRevision.order_id == order_id)
            .order_by(DesignRevision.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _notify_after_approval(self, order: Order) -> None:
        """Send notifications after a design is approved."""
        from app.models.user import User

        # Notify the designer
        if order.assigned_designer_id:
            designer = await self.db.get(User, order.assigned_designer_id)
            if designer and designer.telegram_id:
                await tg_notify_designer_approved(designer.telegram_id, str(order.id))

        # Notify based on where the order went
        user_repo = UserRepository(self.db)
        if order.status == OrderStatus.READY_FOR_PRINT:
            ps_ids = await user_repo.get_printshop_telegram_ids()
            city = order.user.city if order.user else ""
            await tg_notify_printshops(ps_ids, str(order.id), order.quantity, city or "")
        elif order.status == OrderStatus.AWAITING_VALIDATION:
            a_ids = await user_repo.get_admin_telegram_ids()
            cat_name = order.category.name_fa if order.category else "-"
            cust_name = f"{order.user.first_name} {order.user.last_name or ''}".strip() if order.user else "-"
            await tg_notify_admins_validation(a_ids, str(order.id), cust_name, cat_name)

    async def _transition_after_approval(self, order: Order) -> None:
        """Move order to next status after design approval."""
        if order.validation_requested:
            new_status = OrderStatus.AWAITING_VALIDATION
        else:
            new_status = OrderStatus.READY_FOR_PRINT

        order.status = new_status

        log_event(
            event_type="order.status_change",
            order_id=str(order.id),
            new_status=new_status.value,
            reason="design_approved",
        )
