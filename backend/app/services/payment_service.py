"""Payment service for business logic.

This module handles all payment-related business logic including:
- Payment initiation (PSP redirect)
- Payment callbacks and verification
- Card-to-card payment flow (upload receipt, admin approval)
- Payment summary and history

The system supports two payment methods:
1. PSP Gateway (mock implementation)
2. Card-to-card with manual admin approval

Example usage:
    service = PaymentService(db)
    result = await service.initiate_payment(user_id, payment_data)
    # Customer pays and uploads receipt
    await service.upload_receipt(payment_id, user_id, receipt_url)
    # Admin approves
    await service.approve_payment(payment_id, admin_id)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from typing import Optional
from decimal import Decimal

from app.repositories.payment_repository import PaymentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.payment import (
    PaymentInitiate, PaymentInitiateResponse, PaymentCallback, PaymentVerify,
    PaymentOut, PaymentListResponse, PaymentSummary, PendingPaymentOut
)
from app.schemas.order import OrderStatusUpdate
from app.models.enums import PaymentStatus, PaymentType, OrderStatus, UserRole
from app.utils.logger import log_event


# Mock PSP URL (replace with real PSP in production)
MOCK_PSP_URL = "https://sandbox.zarinpal.com/pg/StartPay/"


class PaymentService:
    """Service layer for payment business logic.
    
    Handles payment initiation, verification, and the card-to-card
    approval workflow.
    
    Attributes:
        db: Async database session.
        repository: Payment repository for database operations.
        order_repo: Order repository for order lookups.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize PaymentService with database session."""
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
    
    async def upload_receipt(
        self,
        payment_id: UUID,
        user_id: UUID,
        receipt_image_url: str,
    ) -> PaymentOut:
        """Upload receipt image for card-to-card payment."""
        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        # Verify user owns the payment
        if payment.user_id != user_id:
            raise ValueError("Access denied")
        
        # Check payment status - can only upload for PENDING or FAILED payments
        if payment.status not in [PaymentStatus.PENDING, PaymentStatus.FAILED]:
            raise ValueError("Cannot upload receipt for this payment status")
        
        # Upload receipt
        updated_payment = await self.repository.upload_receipt(
            payment_id=payment_id,
            receipt_image_url=receipt_image_url,
        )
        
        log_event(
            event_type="payment.receipt_uploaded",
            payment_id=str(payment_id),
            order_id=str(payment.order_id),
            user_id=str(user_id),
        )
        
        return PaymentOut.model_validate(updated_payment)
    
    async def approve_payment(
        self,
        payment_id: UUID,
        admin_id: UUID,
    ) -> PaymentOut:
        """Approve a payment (admin action)."""
        # Verify admin role
        user_repo = UserRepository(self.db)
        admin = await user_repo.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise ValueError("Admin access required")
        
        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        # Check payment status
        if payment.status != PaymentStatus.AWAITING_APPROVAL:
            raise ValueError("Payment is not awaiting approval")
        
        # Approve payment
        updated_payment = await self.repository.approve_payment(
            payment_id=payment_id,
            admin_id=admin_id,
        )
        
        log_event(
            event_type="payment.approved",
            payment_id=str(payment_id),
            order_id=str(payment.order_id),
            admin_id=str(admin_id),
            amount=str(payment.amount),
        )
        
        # Update order status if needed
        await self._check_and_update_order_status(payment.order_id)
        
        return PaymentOut.model_validate(updated_payment)
    
    async def reject_payment(
        self,
        payment_id: UUID,
        admin_id: UUID,
        reason: str,
    ) -> PaymentOut:
        """Reject a payment (admin action)."""
        # Verify admin role
        user_repo = UserRepository(self.db)
        admin = await user_repo.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise ValueError("Admin access required")
        
        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        # Check payment status
        if payment.status != PaymentStatus.AWAITING_APPROVAL:
            raise ValueError("Payment is not awaiting approval")
        
        # Reject payment
        updated_payment = await self.repository.reject_payment(
            payment_id=payment_id,
            admin_id=admin_id,
            reason=reason,
        )
        
        log_event(
            event_type="payment.rejected",
            payment_id=str(payment_id),
            order_id=str(payment.order_id),
            admin_id=str(admin_id),
            reason=reason,
        )
        
        return PaymentOut.model_validate(updated_payment)
    
    async def get_pending_approval_payments(
        self,
        admin_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> PaymentListResponse:
        """Get payments awaiting admin approval."""
        # Verify admin role
        user_repo = UserRepository(self.db)
        admin = await user_repo.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise ValueError("Admin access required")
        
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        payments, total = await self.repository.get_pending_approval(
            page=page,
            page_size=page_size,
        )
        
        # Enrich with order and user info
        result_items = []
        for payment in payments:
            order = await self.order_repo.get_by_id(payment.order_id)
            user = await user_repo.get_by_id(payment.user_id)
            
            item = PendingPaymentOut(
                **PaymentOut.model_validate(payment).model_dump(),
                order_short_id=str(payment.order_id)[:8] if payment.order_id else None,
                customer_name=f"{user.first_name} {user.last_name or ''}".strip() if user else None,
                customer_telegram_id=user.telegram_id if user else None,
            )
            result_items.append(item)
        
        return PaymentListResponse(
            items=result_items,
            total=total,
            page=page,
            page_size=page_size,
        )

