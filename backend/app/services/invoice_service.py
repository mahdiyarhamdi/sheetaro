"""Invoice service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceSearchParams,
    InvoiceOut, InvoiceListResponse, InvoiceItem
)
from app.models.enums import OrderStatus
from app.utils.logger import log_event


class InvoiceService:
    """Service layer for invoice business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = InvoiceRepository(db)
        self.order_repo = OrderRepository(db)
    
    async def create_invoice(
        self,
        user_id: UUID,
        invoice_data: InvoiceCreate,
    ) -> InvoiceOut:
        """Create a new invoice."""
        # Verify order exists and belongs to user
        order = await self.order_repo.get_by_id(invoice_data.order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.user_id != user_id:
            raise ValueError("Access denied")
        
        # Verify order is delivered (invoice template can be used)
        if order.status not in [OrderStatus.DELIVERED, OrderStatus.SHIPPED]:
            raise ValueError("Invoice can only be created for delivered orders")
        
        # Create invoice
        invoice = await self.repository.create(user_id, invoice_data)
        
        log_event(
            event_type="invoice.created",
            invoice_id=str(invoice.id),
            invoice_number=invoice.invoice_number,
            user_id=str(user_id),
            order_id=str(invoice_data.order_id),
        )
        
        return self._to_out(invoice)
    
    def _to_out(self, invoice) -> InvoiceOut:
        """Convert invoice model to output schema."""
        return InvoiceOut(
            id=invoice.id,
            order_id=invoice.order_id,
            user_id=invoice.user_id,
            invoice_number=invoice.invoice_number,
            customer_name=invoice.customer_name,
            customer_code=invoice.customer_code,
            customer_address=invoice.customer_address,
            customer_phone=invoice.customer_phone,
            customer_national_id=invoice.customer_national_id,
            items=[InvoiceItem(**item) for item in invoice.items],
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            discount_amount=invoice.discount_amount,
            total_amount=invoice.total_amount,
            issue_date=invoice.issue_date,
            pdf_file_url=invoice.pdf_file_url,
            notes=invoice.notes,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )
    
    async def get_invoice_by_id(self, invoice_id: UUID) -> Optional[InvoiceOut]:
        """Get invoice by ID."""
        invoice = await self.repository.get_by_id(invoice_id)
        if invoice:
            return self._to_out(invoice)
        return None
    
    async def get_invoice_by_number(self, invoice_number: str) -> Optional[InvoiceOut]:
        """Get invoice by invoice number."""
        invoice = await self.repository.get_by_number(invoice_number)
        if invoice:
            return self._to_out(invoice)
        return None
    
    async def get_user_invoices(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> InvoiceListResponse:
        """Get invoices for a user."""
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        invoices, total = await self.repository.get_by_user(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )
        
        return InvoiceListResponse(
            items=[self._to_out(i) for i in invoices],
            total=total,
            page=page,
            page_size=page_size,
        )
    
    async def search_invoices(
        self,
        user_id: UUID,
        search_params: InvoiceSearchParams,
        page: int = 1,
        page_size: int = 20,
        has_subscription: bool = False,
    ) -> InvoiceListResponse:
        """Search invoices with advanced filters (requires subscription)."""
        if not has_subscription:
            raise ValueError("Advanced search requires subscription")
        
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        invoices, total = await self.repository.search(
            user_id=user_id,
            search_params=search_params,
            page=page,
            page_size=page_size,
        )
        
        return InvoiceListResponse(
            items=[self._to_out(i) for i in invoices],
            total=total,
            page=page,
            page_size=page_size,
        )
    
    async def update_invoice(
        self,
        invoice_id: UUID,
        invoice_data: InvoiceUpdate,
        user_id: UUID,
    ) -> Optional[InvoiceOut]:
        """Update invoice."""
        invoice = await self.repository.get_by_id(invoice_id)
        if not invoice:
            return None
        
        if invoice.user_id != user_id:
            raise ValueError("Access denied")
        
        updated_invoice = await self.repository.update(invoice_id, invoice_data)
        if updated_invoice:
            return self._to_out(updated_invoice)
        return None
    
    async def generate_pdf(self, invoice_id: UUID, user_id: UUID) -> str:
        """Generate PDF for invoice (placeholder - actual implementation would use PDF library)."""
        invoice = await self.repository.get_by_id(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        if invoice.user_id != user_id:
            raise ValueError("Access denied")
        
        # Placeholder for PDF generation
        # In real implementation, use reportlab, weasyprint, or similar
        pdf_url = f"/files/invoices/{invoice.invoice_number}.pdf"
        
        await self.repository.set_pdf_url(invoice_id, pdf_url)
        
        log_event(
            event_type="invoice.pdf_generated",
            invoice_id=str(invoice_id),
            invoice_number=invoice.invoice_number,
        )
        
        return pdf_url



