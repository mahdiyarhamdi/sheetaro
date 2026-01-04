"""Invoice API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date
from typing import Optional
from decimal import Decimal

from app.api.deps import get_db
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceSearchParams,
    InvoiceOut, InvoiceListResponse
)
from app.services.invoice_service import InvoiceService

router = APIRouter()


@router.post(
    "/invoices",
    response_model=InvoiceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create invoice",
    description="Create a new invoice record for an order",
)
async def create_invoice(
    invoice_data: InvoiceCreate,
    user_id: UUID = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> InvoiceOut:
    """Create a new invoice."""
    service = InvoiceService(db)
    try:
        return await service.create_invoice(user_id, invoice_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/invoices/{invoice_number}",
    response_model=InvoiceOut,
    summary="Get invoice by number",
    description="Get invoice by invoice number",
)
async def get_invoice_by_number(
    invoice_number: str,
    db: AsyncSession = Depends(get_db),
) -> InvoiceOut:
    """Get invoice by number."""
    service = InvoiceService(db)
    invoice = await service.get_invoice_by_number(invoice_number)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with number {invoice_number} not found"
        )
    return invoice


@router.get(
    "/invoices",
    response_model=InvoiceListResponse,
    summary="List user invoices",
    description="Get list of invoices for a user",
)
async def list_invoices(
    user_id: UUID = Query(..., description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> InvoiceListResponse:
    """List invoices for a user."""
    service = InvoiceService(db)
    return await service.get_user_invoices(user_id, page, page_size)


@router.get(
    "/invoices/search",
    response_model=InvoiceListResponse,
    summary="Search invoices",
    description="Advanced search for invoices (requires subscription)",
)
async def search_invoices(
    user_id: UUID = Query(..., description="User ID"),
    customer_name: Optional[str] = Query(None, description="Customer name"),
    invoice_number: Optional[str] = Query(None, description="Invoice number"),
    date_from: Optional[date] = Query(None, description="From date"),
    date_to: Optional[date] = Query(None, description="To date"),
    amount_min: Optional[Decimal] = Query(None, description="Minimum amount"),
    amount_max: Optional[Decimal] = Query(None, description="Maximum amount"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    has_subscription: bool = Query(False, description="User has active subscription"),
    db: AsyncSession = Depends(get_db),
) -> InvoiceListResponse:
    """Search invoices with advanced filters."""
    search_params = InvoiceSearchParams(
        customer_name=customer_name,
        invoice_number=invoice_number,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
    )
    
    service = InvoiceService(db)
    try:
        return await service.search_invoices(
            user_id, search_params, page, page_size, has_subscription
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.patch(
    "/invoices/{invoice_id}",
    response_model=InvoiceOut,
    summary="Update invoice",
    description="Update invoice details",
)
async def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceUpdate,
    user_id: UUID = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> InvoiceOut:
    """Update invoice."""
    service = InvoiceService(db)
    try:
        invoice = await service.update_invoice(invoice_id, invoice_data, user_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice with id {invoice_id} not found"
            )
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/invoices/{invoice_id}/pdf",
    response_model=dict,
    summary="Generate PDF",
    description="Generate PDF file for invoice",
)
async def generate_pdf(
    invoice_id: UUID,
    user_id: UUID = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate PDF for invoice."""
    service = InvoiceService(db)
    try:
        pdf_url = await service.generate_pdf(invoice_id, user_id)
        return {"pdf_url": pdf_url}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )




