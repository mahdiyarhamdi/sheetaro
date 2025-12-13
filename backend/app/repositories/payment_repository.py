"""Payment repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal

from app.models.payment import Payment
from app.models.enums import PaymentStatus, PaymentType
from app.schemas.payment import PaymentVerify


class PaymentRepository:
    """Repository for payment database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        order_id: UUID,
        user_id: UUID,
        payment_type: PaymentType,
        amount: Decimal,
        authority: str,
        description: Optional[str] = None,
    ) -> Payment:
        """Create a new payment."""
        payment = Payment(
            order_id=order_id,
            user_id=user_id,
            type=payment_type,
            amount=amount,
            authority=authority,
            description=description,
            status=PaymentStatus.PENDING,
        )
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment
    
    async def get_by_id(self, payment_id: UUID) -> Optional[Payment]:
        """Get payment by ID."""
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_authority(self, authority: str) -> Optional[Payment]:
        """Get payment by PSP authority."""
        result = await self.db.execute(
            select(Payment).where(Payment.authority == authority)
        )
        return result.scalar_one_or_none()
    
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID."""
        result = await self.db.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_order(
        self,
        order_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Payment], int]:
        """Get payments for an order."""
        query = select(Payment).where(Payment.order_id == order_id)
        count_query = select(func.count(Payment.id)).where(Payment.order_id == order_id)
        
        query = query.order_by(Payment.created_at.desc())
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        payments = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return payments, total
    
    async def get_by_user(
        self,
        user_id: UUID,
        status: Optional[PaymentStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Payment], int]:
        """Get payments for a user."""
        query = select(Payment).where(Payment.user_id == user_id)
        count_query = select(func.count(Payment.id)).where(Payment.user_id == user_id)
        
        if status:
            query = query.where(Payment.status == status)
            count_query = count_query.where(Payment.status == status)
        
        query = query.order_by(Payment.created_at.desc())
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        payments = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return payments, total
    
    async def update_status(
        self,
        payment_id: UUID,
        verify_data: PaymentVerify,
    ) -> Optional[Payment]:
        """Update payment status after verification."""
        update_data = {
            'status': verify_data.status,
        }
        
        if verify_data.ref_id:
            update_data['ref_id'] = verify_data.ref_id
        if verify_data.card_pan:
            update_data['card_pan'] = verify_data.card_pan
        
        if verify_data.status == PaymentStatus.SUCCESS:
            update_data['paid_at'] = datetime.now(timezone.utc)
        
        await self.db.execute(
            update(Payment)
            .where(Payment.id == payment_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(payment_id)
    
    async def get_order_payment_summary(self, order_id: UUID) -> dict:
        """Get payment summary for an order."""
        # Get total paid
        paid_query = select(func.sum(Payment.amount)).where(
            Payment.order_id == order_id,
            Payment.status == PaymentStatus.SUCCESS,
        )
        paid_result = await self.db.execute(paid_query)
        total_paid = paid_result.scalar() or Decimal('0')
        
        # Get total pending
        pending_query = select(func.sum(Payment.amount)).where(
            Payment.order_id == order_id,
            Payment.status == PaymentStatus.PENDING,
        )
        pending_result = await self.db.execute(pending_query)
        total_pending = pending_result.scalar() or Decimal('0')
        
        return {
            'total_paid': total_paid,
            'total_pending': total_pending,
        }

