"""Validation service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.repositories.validation_repository import ValidationRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.validation import (
    ValidationRequestCreate, ValidationReportCreate,
    ValidationReportOut, ValidationReportListResponse, ValidationIssue
)
from app.schemas.order import OrderStatusUpdate
from app.models.enums import OrderStatus, ValidationStatus, UserRole
from app.utils.logger import log_event


class ValidationService:
    """Service layer for validation business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ValidationRepository(db)
        self.order_repo = OrderRepository(db)
        self.user_repo = UserRepository(db)
    
    async def request_validation(
        self,
        user_id: UUID,
        request_data: ValidationRequestCreate,
    ) -> dict:
        """Request validation for an order."""
        # Get order
        order = await self.order_repo.get_by_id(request_data.order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Verify user owns the order
        if order.user_id != user_id:
            raise ValueError("Access denied")
        
        # Check if validation can be requested
        if order.validation_requested:
            raise ValueError("Validation already requested")
        
        # Update order to awaiting validation
        from sqlalchemy import update
        from app.models.order import Order
        
        await self.db.execute(
            update(Order)
            .where(Order.id == order.id)
            .values(
                validation_requested=True,
                validation_status=ValidationStatus.PENDING,
                status=OrderStatus.AWAITING_VALIDATION,
            )
        )
        await self.db.flush()
        
        log_event(
            event_type="validation.requested",
            order_id=str(order.id),
            user_id=str(user_id),
        )
        
        return {"message": "Validation requested successfully", "order_id": str(order.id)}
    
    async def submit_report(
        self,
        validator_id: UUID,
        report_data: ValidationReportCreate,
    ) -> ValidationReportOut:
        """Submit a validation report."""
        # Verify validator role
        validator = await self.user_repo.get_by_id(validator_id)
        if not validator or validator.role != UserRole.VALIDATOR:
            raise ValueError("User is not a validator")
        
        # Get order
        order = await self.order_repo.get_by_id(report_data.order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Check order is awaiting validation
        if order.status != OrderStatus.AWAITING_VALIDATION:
            raise ValueError("Order is not awaiting validation")
        
        # Create report
        report = await self.repository.create(validator_id, report_data)
        
        # Update order validation status and assign validator
        from sqlalchemy import update
        from app.models.order import Order
        
        new_validation_status = ValidationStatus.PASSED if report_data.passed == "PASSED" else ValidationStatus.FAILED
        new_order_status = OrderStatus.READY_FOR_PRINT if report_data.passed == "PASSED" else OrderStatus.NEEDS_ACTION
        
        await self.db.execute(
            update(Order)
            .where(Order.id == order.id)
            .values(
                assigned_validator_id=validator_id,
                validation_status=new_validation_status,
                status=new_order_status,
            )
        )
        await self.db.flush()
        
        log_event(
            event_type="validation.report_submitted",
            order_id=str(order.id),
            validator_id=str(validator_id),
            passed=report_data.passed,
            issues_count=len(report_data.issues),
        )
        
        return ValidationReportOut.model_validate(report)
    
    async def get_report_by_id(self, report_id: UUID) -> Optional[ValidationReportOut]:
        """Get validation report by ID."""
        report = await self.repository.get_by_id(report_id)
        if report:
            # Convert issues from dict to ValidationIssue objects
            report_out = ValidationReportOut(
                id=report.id,
                order_id=report.order_id,
                validator_id=report.validator_id,
                issues=[ValidationIssue(**issue) for issue in report.issues],
                fix_cost=report.fix_cost,
                summary=report.summary,
                passed=report.passed,
                created_at=report.created_at,
                updated_at=report.updated_at,
            )
            return report_out
        return None
    
    async def get_order_reports(
        self,
        order_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> ValidationReportListResponse:
        """Get validation reports for an order."""
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        reports, total = await self.repository.get_by_order(
            order_id=order_id,
            page=page,
            page_size=page_size,
        )
        
        items = []
        for report in reports:
            items.append(ValidationReportOut(
                id=report.id,
                order_id=report.order_id,
                validator_id=report.validator_id,
                issues=[ValidationIssue(**issue) for issue in report.issues],
                fix_cost=report.fix_cost,
                summary=report.summary,
                passed=report.passed,
                created_at=report.created_at,
                updated_at=report.updated_at,
            ))
        
        return ValidationReportListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

