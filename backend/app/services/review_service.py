"""Service layer for order reviews and ratings."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.models.order import Order
from app.models.enums import OrderStatus, ReviewType
from app.repositories.order_repository import OrderRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.schemas.review import ReviewCreate, ReviewOut, ReviewListResponse
from app.schemas.order import OrderOut

logger = logging.getLogger(__name__)


def _review_to_out(review, user_name: str = "کاربر", user_phone: Optional[str] = None) -> ReviewOut:
    """Helper to convert Review model to ReviewOut schema."""
    return ReviewOut(
        id=review.id,
        order_id=review.order_id,
        user_id=review.user_id,
        printshop_id=review.printshop_id,
        designer_id=review.designer_id,
        review_type=review.review_type.value if review.review_type else "PRINTSHOP",
        rating=review.rating,
        comment=review.comment,
        is_approved=review.is_approved,
        created_at=review.created_at,
        updated_at=review.updated_at,
        user_name=user_name,
        user_phone=user_phone,
    )


class ReviewService:
    """Service for review business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize ReviewService with database session."""
        self.db = db
        self.order_repo = OrderRepository(db)
        self.review_repo = ReviewRepository(db)
        self.user_repo = UserRepository(db)

    async def _get_user_display(self, user_id: UUID) -> tuple[str, Optional[str]]:
        """Get user name and phone for display."""
        user = await self.user_repo.get_by_id(user_id)
        name = user.full_name or user.username or "کاربر" if user else "کاربر"
        phone = user.phone_number if user else None
        return name, phone

    async def confirm_delivery(
        self,
        order_id: UUID,
        user_id: UUID,
    ) -> OrderOut:
        """Customer confirms delivery of a shipped order."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("سفارش یافت نشد")

        if order.user_id != user_id:
            raise PermissionError("این سفارش متعلق به شما نیست")

        if order.status != OrderStatus.SHIPPED:
            raise ValueError(
                f"فقط سفارش‌های ارسال‌شده قابل تایید تحویل هستند. وضعیت فعلی: {order.status.value}"
            )

        now = datetime.now(timezone.utc)
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(status=OrderStatus.DELIVERED, delivered_at=now)
        )
        await self.db.flush()

        updated_order = await self.order_repo.get_by_id(order_id)
        logger.info(
            "order.delivery_confirmed",
            extra={"order_id": str(order_id), "user_id": str(user_id)},
        )
        return OrderOut.model_validate(updated_order)

    async def submit_review(
        self,
        order_id: UUID,
        user_id: UUID,
        review_data: ReviewCreate,
    ) -> ReviewOut:
        """Customer submits a review for a delivered order."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("سفارش یافت نشد")

        if order.user_id != user_id:
            raise PermissionError("این سفارش متعلق به شما نیست")

        if order.status != OrderStatus.DELIVERED:
            raise ValueError("فقط سفارش‌های تحویل‌شده قابل نظردهی هستند")

        # Determine review type
        rt_str = review_data.review_type or "PRINTSHOP"
        try:
            review_type = ReviewType(rt_str)
        except ValueError:
            review_type = ReviewType.PRINTSHOP

        # Check for existing review of this type
        existing = await self.review_repo.get_by_order_id(order_id, review_type=review_type)
        if existing:
            target = "چاپخانه" if review_type == ReviewType.PRINTSHOP else "طراح"
            raise ValueError(f"شما قبلا برای {target} این سفارش نظر ثبت کرده‌اید")

        # Validate the target exists on the order
        printshop_id = None
        designer_id = None
        if review_type == ReviewType.PRINTSHOP:
            if not order.assigned_printshop_id:
                raise ValueError("چاپخانه‌ای به این سفارش اختصاص داده نشده است")
            printshop_id = order.assigned_printshop_id
        else:
            if not order.assigned_designer_id:
                raise ValueError("طراحی به این سفارش اختصاص داده نشده است")
            designer_id = order.assigned_designer_id

        review = await self.review_repo.create(
            order_id=order_id,
            user_id=user_id,
            printshop_id=printshop_id,
            designer_id=designer_id,
            review_type=review_type,
            rating=review_data.rating,
            comment=review_data.comment,
        )
        await self.db.commit()

        user_name, user_phone = await self._get_user_display(user_id)

        logger.info(
            "review.submitted",
            extra={
                "order_id": str(order_id),
                "user_id": str(user_id),
                "review_type": review_type.value,
                "rating": review_data.rating,
            },
        )

        return _review_to_out(review, user_name, user_phone)

    async def get_review_for_order(
        self,
        order_id: UUID,
        review_type: Optional[ReviewType] = None,
    ) -> Optional[ReviewOut]:
        """Get the review for a specific order (optionally by type)."""
        review = await self.review_repo.get_by_order_id(order_id, review_type=review_type)
        if not review:
            return None
        user_name, user_phone = await self._get_user_display(review.user_id)
        return _review_to_out(review, user_name, user_phone)

    async def get_reviews_for_order(self, order_id: UUID) -> list[ReviewOut]:
        """Get all reviews (printshop + designer) for an order."""
        reviews = await self.review_repo.get_reviews_for_order(order_id)
        items = []
        for review in reviews:
            user_name, user_phone = await self._get_user_display(review.user_id)
            items.append(_review_to_out(review, user_name, user_phone))
        return items

    async def list_reviews(
        self,
        printshop_id: Optional[UUID] = None,
        designer_id: Optional[UUID] = None,
        is_approved: Optional[bool] = None,
        review_type: Optional[ReviewType] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ReviewListResponse:
        """List reviews with optional filters (admin)."""
        reviews, total = await self.review_repo.list_all(
            printshop_id=printshop_id,
            designer_id=designer_id,
            is_approved=is_approved,
            review_type=review_type,
            page=page,
            page_size=page_size,
        )

        items = []
        for review in reviews:
            user_name, user_phone = await self._get_user_display(review.user_id)
            items.append(_review_to_out(review, user_name, user_phone))

        return ReviewListResponse(items=items, total=total, page=page, page_size=page_size)

    async def approve_review(self, review_id: UUID) -> Optional[ReviewOut]:
        """Admin approves a review."""
        review = await self.review_repo.approve(review_id)
        if not review:
            return None
        user_name, user_phone = await self._get_user_display(review.user_id)
        logger.info("review.approved", extra={"review_id": str(review_id)})
        return _review_to_out(review, user_name, user_phone)

    async def reject_review(self, review_id: UUID) -> bool:
        """Admin rejects (deletes) a review."""
        result = await self.review_repo.reject(review_id)
        if result:
            await self.db.commit()
            logger.info("review.rejected", extra={"review_id": str(review_id)})
        return result
