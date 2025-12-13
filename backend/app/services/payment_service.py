"""Payment service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from typing import Optional
from decimal import Decimal

from app.repositories.payment_repository import PaymentRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.payment import (
    PaymentInitiate, PaymentInitiateResponse, PaymentCallback, PaymentVerify,
    PaymentOut, PaymentListResponse, PaymentSummary
)
from app.schemas.order import OrderStatusUpdate
from app.models.enums import PaymentStatus, PaymentType, OrderStatus
from app.utils.logger import log_event


# Mock PSP URL (replace with real PSP in production)
MOCK_PSP_URL = "https://sandbox.zarinpal.com/pg/StartPay/"


class PaymentService:
    """Service layer for payment business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PaymentRepository(db)
        self.order_repo = OrderRepository(db)
    
    def _get_payment_amount(self, order, payment_type: PaymentType) -> Decimal:
        """Get payment amount based on type."""
        if payment_type == PaymentType.VALIDATION:
            return order.validation_price
        elif payment_type == PaymentType.DESIGN:
            return order.design_price
        elif payment_type == PaymentType.FIX:
            return order.fix_price
        elif payment_type == PaymentType.PRINT:
            return order.print_price
        else:
            return order.total_price
    
    async def initiate_payment(
        self,
        user_id: UUID,
        payment_data: PaymentInitiate,
    ) -> PaymentInitiateResponse:
        """Initiate a payment and get PSP redirect URL."""
        # Get order
        order = await self.order_repo.get_by_id(payment_data.order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Verify user owns the order
        if order.user_id != user_id:
            raise ValueError("Access denied")
        
        # Get amount based on payment type
        amount = self._get_payment_amount(order, payment_data.type)
        if amount <= 0:
            raise ValueError("Invalid payment amount")
        
        # Generate authority (in real implementation, call PSP API)
        authority = f"A{uuid4().hex[:32]}"
        
        # Create payment record
        payment = await self.repository.create(
            order_id=order.id,
            user_id=user_id,
            payment_type=payment_data.type,
            amount=amount,
            authority=authority,
            description=f"پرداخت {payment_data.type.value} برای سفارش {order.id}",
        )
        
        log_event(
            event_type="payment.initiated",
            payment_id=str(payment.id),
            order_id=str(order.id),
            user_id=str(user_id),
            amount=str(amount),
            type=payment_data.type.value,
        )
        
        # Generate redirect URL (mock)
        redirect_url = f"{MOCK_PSP_URL}{authority}"
        
        return PaymentInitiateResponse(
            payment_id=payment.id,
            authority=authority,
            redirect_url=redirect_url,
            amount=amount,
        )
    
    async def handle_callback(
        self,
        callback_data: PaymentCallback,
    ) -> PaymentOut:
        """Handle payment callback from PSP."""
        # Find payment by authority
        payment = await self.repository.get_by_authority(callback_data.authority)
        if not payment:
            raise ValueError("Payment not found")
        
        # Already processed
        if payment.status != PaymentStatus.PENDING:
            return PaymentOut.model_validate(payment)
        
        # Determine status based on callback
        # In real implementation, verify with PSP API
        if callback_data.status.upper() == "OK":
            new_status = PaymentStatus.SUCCESS
        else:
            new_status = PaymentStatus.FAILED
        
        # Update payment
        verify_data = PaymentVerify(
            authority=callback_data.authority,
            status=new_status,
            ref_id=callback_data.ref_id,
        )
        
        updated_payment = await self.repository.update_status(payment.id, verify_data)
        
        log_event(
            event_type="payment.callback",
            payment_id=str(payment.id),
            order_id=str(payment.order_id),
            status=new_status.value,
            ref_id=callback_data.ref_id,
        )
        
        # Update order status if all payments are successful
        if new_status == PaymentStatus.SUCCESS:
            await self._check_and_update_order_status(payment.order_id)
        
        return PaymentOut.model_validate(updated_payment)
    
    async def _check_and_update_order_status(self, order_id: UUID) -> None:
        """Check if all payments are complete and update order status."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return
        
        summary = await self.repository.get_order_payment_summary(order_id)
        
        # If total paid >= total price, move order forward
        if summary['total_paid'] >= order.total_price:
            # Determine next status based on current status
            if order.status == OrderStatus.PENDING:
                if order.validation_requested:
                    new_status = OrderStatus.AWAITING_VALIDATION
                else:
                    new_status = OrderStatus.READY_FOR_PRINT
                
                status_update = OrderStatusUpdate(status=new_status)
                await self.order_repo.update_status(order_id, status_update)
                
                log_event(
                    event_type="order.status_change",
                    order_id=str(order_id),
                    new_status=new_status.value,
                    reason="payment_complete",
                )
    
    async def get_payment_by_id(self, payment_id: UUID) -> Optional[PaymentOut]:
        """Get payment by ID."""
        payment = await self.repository.get_by_id(payment_id)
        if payment:
            return PaymentOut.model_validate(payment)
        return None
    
    async def get_order_payments(
        self,
        order_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> PaymentListResponse:
        """Get payments for an order."""
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        payments, total = await self.repository.get_by_order(
            order_id=order_id,
            page=page,
            page_size=page_size,
        )
        
        return PaymentListResponse(
            items=[PaymentOut.model_validate(p) for p in payments],
            total=total,
            page=page,
            page_size=page_size,
        )
    
    async def get_payment_summary(self, order_id: UUID) -> PaymentSummary:
        """Get payment summary for an order."""
        payments, _ = await self.repository.get_by_order(order_id, page=1, page_size=100)
        summary = await self.repository.get_order_payment_summary(order_id)
        
        return PaymentSummary(
            order_id=order_id,
            total_paid=summary['total_paid'],
            total_pending=summary['total_pending'],
            payments=[PaymentOut.model_validate(p) for p in payments],
        )

