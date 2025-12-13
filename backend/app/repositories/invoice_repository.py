"""Invoice repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from typing import Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
import random
import string

from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceSearchParams


class InvoiceRepository:
    """Repository for invoice database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _generate_invoice_number(self) -> str:
        """Generate a unique invoice number."""
        # Format: INV-YYYYMMDD-XXXXX
        from datetime import datetime
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.digits, k=5))
        return f"INV-{date_part}-{random_part}"
    
    async def create(
        self,
        user_id: UUID,
        invoice_data: InvoiceCreate,
    ) -> Invoice:
        """Create a new invoice."""
        # Calculate subtotal
        items_data = [item.model_dump() for item in invoice_data.items]
        subtotal = sum(Decimal(str(item['total'])) for item in items_data)
        total_amount = subtotal + invoice_data.tax_amount - invoice_data.discount_amount
        
        # Generate unique invoice number
        invoice_number = self._generate_invoice_number()
        
        invoice = Invoice(
            order_id=invoice_data.order_id,
            user_id=user_id,
            invoice_number=invoice_number,
            customer_name=invoice_data.customer_name,
            customer_code=invoice_data.customer_code,
            customer_address=invoice_data.customer_address,
            customer_phone=invoice_data.customer_phone,
            customer_national_id=invoice_data.customer_national_id,
            items=items_data,
            subtotal=subtotal,
            tax_amount=invoice_data.tax_amount,
            discount_amount=invoice_data.discount_amount,
            total_amount=total_amount,
            issue_date=invoice_data.issue_date,
            notes=invoice_data.notes,
        )
        self.db.add(invoice)
        await self.db.flush()
        await self.db.refresh(invoice)
        return invoice
    
    async def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get invoice by ID."""
        result = await self.db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number."""
        result = await self.db.execute(
            select(Invoice).where(Invoice.invoice_number == invoice_number)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Invoice], int]:
        """Get invoices for a user."""
        query = select(Invoice).where(Invoice.user_id == user_id)
        count_query = select(func.count(Invoice.id)).where(Invoice.user_id == user_id)
        
        query = query.order_by(Invoice.created_at.desc())
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        invoices = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return invoices, total
    
    async def search(
        self,
        user_id: UUID,
        search_params: InvoiceSearchParams,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Invoice], int]:
        """Search invoices with advanced filters (subscription feature)."""
        conditions = [Invoice.user_id == user_id]
        
        if search_params.customer_name:
            conditions.append(Invoice.customer_name.ilike(f"%{search_params.customer_name}%"))
        
        if search_params.invoice_number:
            conditions.append(Invoice.invoice_number.ilike(f"%{search_params.invoice_number}%"))
        
        if search_params.date_from:
            conditions.append(Invoice.issue_date >= search_params.date_from)
        
        if search_params.date_to:
            conditions.append(Invoice.issue_date <= search_params.date_to)
        
        if search_params.amount_min:
            conditions.append(Invoice.total_amount >= search_params.amount_min)
        
        if search_params.amount_max:
            conditions.append(Invoice.total_amount <= search_params.amount_max)
        
        query = select(Invoice).where(and_(*conditions))
        count_query = select(func.count(Invoice.id)).where(and_(*conditions))
        
        query = query.order_by(Invoice.issue_date.desc())
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        invoices = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return invoices, total
    
    async def update(self, invoice_id: UUID, invoice_data: InvoiceUpdate) -> Optional[Invoice]:
        """Update invoice."""
        update_data = invoice_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(invoice_id)
        
        # If items are updated, recalculate totals
        if 'items' in update_data:
            items_data = [item.model_dump() for item in invoice_data.items]
            update_data['items'] = items_data
            subtotal = sum(Decimal(str(item['total'])) for item in items_data)
            update_data['subtotal'] = subtotal
            
            invoice = await self.get_by_id(invoice_id)
            if invoice:
                tax = update_data.get('tax_amount', invoice.tax_amount)
                discount = update_data.get('discount_amount', invoice.discount_amount)
                update_data['total_amount'] = subtotal + tax - discount
        
        await self.db.execute(
            update(Invoice)
            .where(Invoice.id == invoice_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(invoice_id)
    
    async def set_pdf_url(self, invoice_id: UUID, pdf_url: str) -> Optional[Invoice]:
        """Set PDF file URL for invoice."""
        await self.db.execute(
            update(Invoice)
            .where(Invoice.id == invoice_id)
            .values(pdf_file_url=pdf_url)
        )
        await self.db.flush()
        return await self.get_by_id(invoice_id)

