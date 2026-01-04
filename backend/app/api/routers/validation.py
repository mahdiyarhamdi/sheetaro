"""Validation API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.schemas.validation import (
    ValidationRequestCreate, ValidationReportCreate,
    ValidationReportOut, ValidationReportListResponse
)
from app.services.validation_service import ValidationService

router = APIRouter()


@router.post(
    "/validation/request",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Request validation",
    description="Request design/file validation for an order",
)
async def request_validation(
    request_data: ValidationRequestCreate,
    user_id: UUID = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Request validation for an order."""
    service = ValidationService(db)
    try:
        return await service.request_validation(user_id, request_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/validation/{order_id}/report",
    response_model=ValidationReportOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit validation report",
    description="Submit validation report (Validator only)",
)
async def submit_report(
    order_id: UUID,
    report_data: ValidationReportCreate,
    validator_id: UUID = Query(..., description="Validator user ID"),
    db: AsyncSession = Depends(get_db),
) -> ValidationReportOut:
    """Submit validation report."""
    # Ensure order_id in path matches body
    if report_data.order_id != order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order ID mismatch"
        )
    
    service = ValidationService(db)
    try:
        return await service.submit_report(validator_id, report_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/validation/{report_id}",
    response_model=ValidationReportOut,
    summary="Get validation report",
    description="Get validation report by ID",
)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ValidationReportOut:
    """Get validation report by ID."""
    service = ValidationService(db)
    report = await service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation report with id {report_id} not found"
        )
    return report


@router.get(
    "/validation/order/{order_id}",
    response_model=ValidationReportListResponse,
    summary="Get order validation reports",
    description="Get all validation reports for an order",
)
async def get_order_reports(
    order_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> ValidationReportListResponse:
    """Get validation reports for an order."""
    service = ValidationService(db)
    return await service.get_order_reports(order_id, page, page_size)




