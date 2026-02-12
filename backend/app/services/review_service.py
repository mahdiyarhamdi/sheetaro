"""Service layer for order reviews and ratings."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.models.order import Order
from app.models.enums import OrderStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.schemas.review import ReviewCreate, ReviewOut, ReviewListResponse
from app.schemas.order import OrderOut

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for review business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize ReviewService with database session."""
        self.db = db
        self.order_repo = OrderRepository(db)
        self.review_repo = ReviewRepository(db)
        self.user_repo = UserRepository(db)

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

        # Check for existing review
        existing = await self.review_repo.get_by_order_id(order_id)
        if existing:
            raise ValueError("شما قبلا برای این سفارش نظر ثبت کرده‌اید")

        if not order.assigned_printshop_id:
            raise ValueError("چاپخانه‌ای به این سفارش اختصاص داده نشده است")

        review = await self.review_repo.create(
            order_id=order_id,
            user_id=user_id,
            printshop_id=order.assigned_printshop_id,
            rating=review_data.rating,
            comment=review_data.comment,
        )
        await self.db.commit()

        # Get user name for response
        user = await self.user_repo.get_by_id(user_id)
        user_name = user.full_name or user.username or "کاربر" if user else "کاربر"
        user_phone = user.phone_number if user else None

        logger.info(
            "review.submitted",
            extra={
                "order_id": str(order_id),
                "user_id": str(user_id),
                "rating": review_data.rating,
            },
        )

        return ReviewOut(
            id=review.id,
            order_id=review.order_id,
            user_id=review.user_id,
            printshop_id=review.printshop_id,
            rating=review.rating,
            comment=review.comment,
            is_approved=review.is_approved,
            created_at=review.created_at,
            updated_at=review.updated_at,
            user_name=user_name,
            user_phone=user_phone,
        )

    async def get_review_for_order(self, order_id: UUID) -> Optional[ReviewOut]:
        """Get the review for a specific order."""
        review = await self.review_repo.get_by_order_id(order_id)
        if not review:
            return None

        user = await self.user_repo.get_by_id(review.user_id)
        user_name = user.full_name or user.username or "کاربر" if user else "کاربر"
        user_phone = user.phone_number if user else None

        return ReviewOut(
            id=review.id,
            order_id=review.order_id,
            user_id=review.user_id,
            printshop_id=review.printshop_id,
            rating=review.rating,
            comment=review.comment,
            is_approved=review.is_approved,
            created_at=review.created_at,
            updated_at=review.updated_at,
            user_name=user_name,
            user_phone=user_phone,
        )

    async def list_reviews(
        self,
        printshop_id: Optional[UUID] = None,
        is_approved: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ReviewListResponse:
        """List reviews with optional filters (admin)."""
        reviews, total = await self.review_repo.list_all(
            printshop_id=printshop_id,
            is_approved=is_approved,
            page=page,
            page_size=page_size,
        )

        items = []
        for review in reviews:
            user = await self.user_repo.get_by_id(review.user_id)
            user_name = user.full_name or user.username or "کاربر" if user else "کاربر"
            user_phone = user.phone_number if user else None

            items.append(ReviewOut(
                id=review.id,
                order_id=review.order_id,
                user_id=review.user_id,
                printshop_id=review.printshop_id,
                rating=review.rating,
                comment=review.comment,
                is_approved=review.is_approved,
                created_at=review.created_at,
                updated_at=review.updated_at,
                user_name=user_name,
                user_phone=user_phone,
            ))

        return ReviewListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def approve_review(self, review_id: UUID) -> Optional[ReviewOut]:
        """Admin approves a review."""
        review = await self.review_repo.approve(review_id)
        if not review:
            return None

        user = await self.user_repo.get_by_id(review.user_id)
        user_name = user.full_name or user.username or "کاربر" if user else "کاربر"
        user_phone = user.phone_number if user else None

        logger.info(
            "review.approved",
            extra={"review_id": str(review_id)},
        )

        return ReviewOut(
            id=review.id,
            order_id=review.order_id,
            user_id=review.user_id,
            printshop_id=review.printshop_id,
            rating=review.rating,
            comment=review.comment,
            is_approved=review.is_approved,
            created_at=review.created_at,
            updated_at=review.updated_at,
            user_name=user_name,
            user_phone=user_phone,
        )

    async def reject_review(self, review_id: UUID) -> bool:
        """Admin rejects (deletes) a review."""
        result = await self.review_repo.reject(review_id)
        if result:
            await self.db.commit()
            logger.info(
                "review.rejected",
                extra={"review_id": str(review_id)},
            )
        return result
