"""Review repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, delete
from typing import Optional, List, Dict, Tuple
from uuid import UUID

from app.models.review import Review


class ReviewRepository:
    """Repository for review database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        order_id: UUID,
        user_id: UUID,
        printshop_id: UUID,
        rating: int,
        comment: Optional[str] = None,
    ) -> Review:
        """Create a new review."""
        review = Review(
            order_id=order_id,
            user_id=user_id,
            printshop_id=printshop_id,
            rating=rating,
            comment=comment,
        )
        self.db.add(review)
        await self.db.flush()
        await self.db.refresh(review)
        return review

    async def get_by_id(self, review_id: UUID) -> Optional[Review]:
        """Get a review by ID."""
        result = await self.db.execute(
            select(Review).where(Review.id == review_id)
        )
        return result.scalar_one_or_none()

    async def get_by_order_id(self, order_id: UUID) -> Optional[Review]:
        """Get a review by order ID (one review per order)."""
        result = await self.db.execute(
            select(Review).where(Review.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def list_by_printshop(
        self,
        printshop_id: UUID,
        is_approved: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Review], int]:
        """List reviews for a specific print shop with pagination."""
        conditions = [Review.printshop_id == printshop_id]
        if is_approved is not None:
            conditions.append(Review.is_approved == is_approved)

        # Count query
        count_result = await self.db.execute(
            select(func.count(Review.id)).where(*conditions)
        )
        total = count_result.scalar() or 0

        # Data query
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Review)
            .where(*conditions)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        reviews = list(result.scalars().all())

        return reviews, total

    async def list_all(
        self,
        printshop_id: Optional[UUID] = None,
        is_approved: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Review], int]:
        """List all reviews with optional filters and pagination."""
        conditions = []
        if printshop_id:
            conditions.append(Review.printshop_id == printshop_id)
        if is_approved is not None:
            conditions.append(Review.is_approved == is_approved)

        # Count query
        count_stmt = select(func.count(Review.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Data query
        offset = (page - 1) * page_size
        data_stmt = (
            select(Review)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        if conditions:
            data_stmt = data_stmt.where(*conditions)
        result = await self.db.execute(data_stmt)
        reviews = list(result.scalars().all())

        return reviews, total

    async def approve(self, review_id: UUID) -> Optional[Review]:
        """Approve a review."""
        await self.db.execute(
            update(Review)
            .where(Review.id == review_id)
            .values(is_approved=True)
        )
        await self.db.flush()
        return await self.get_by_id(review_id)

    async def reject(self, review_id: UUID) -> bool:
        """Reject (delete) a review."""
        result = await self.db.execute(
            delete(Review).where(Review.id == review_id)
        )
        await self.db.flush()
        return result.rowcount > 0

    async def get_avg_rating(self, printshop_id: UUID) -> Tuple[Optional[float], int]:
        """Get average rating and count for a printshop (approved reviews only)."""
        result = await self.db.execute(
            select(
                func.avg(Review.rating),
                func.count(Review.id),
            ).where(
                Review.printshop_id == printshop_id,
                Review.is_approved == True,
            )
        )
        row = result.one()
        avg = float(row[0]) if row[0] is not None else None
        count = row[1] or 0
        return avg, count

    async def get_avg_ratings_bulk(self, printshop_ids: List[UUID]) -> Dict[UUID, Tuple[Optional[float], int]]:
        """Get average ratings for multiple printshops at once."""
        if not printshop_ids:
            return {}

        result = await self.db.execute(
            select(
                Review.printshop_id,
                func.avg(Review.rating),
                func.count(Review.id),
            ).where(
                Review.printshop_id.in_(printshop_ids),
                Review.is_approved == True,
            ).group_by(Review.printshop_id)
        )
        ratings = {}
        for row in result.all():
            avg = float(row[1]) if row[1] is not None else None
            ratings[row[0]] = (avg, row[2] or 0)
        return ratings
