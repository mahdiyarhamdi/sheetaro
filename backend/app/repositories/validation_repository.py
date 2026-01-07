"""Validation repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID

from app.models.validation import ValidationReport
from app.schemas.validation import ValidationReportCreate


class ValidationRepository:
    """Repository for validation database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        validator_id: UUID,
        report_data: ValidationReportCreate,
    ) -> ValidationReport:
        """Create a new validation report."""
        # Convert issues to dict format
        issues_data = [issue.model_dump() for issue in report_data.issues]
        
        report = ValidationReport(
            order_id=report_data.order_id,
            validator_id=validator_id,
            issues=issues_data,
            fix_cost=report_data.fix_cost,
            summary=report_data.summary,
            passed=report_data.passed,
        )
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report
    
    async def get_by_id(self, report_id: UUID) -> Optional[ValidationReport]:
        """Get validation report by ID."""
        result = await self.db.execute(
            select(ValidationReport).where(ValidationReport.id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_order(
        self,
        order_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ValidationReport], int]:
        """Get validation reports for an order."""
        query = select(ValidationReport).where(ValidationReport.order_id == order_id)
        count_query = select(func.count(ValidationReport.id)).where(ValidationReport.order_id == order_id)
        
        query = query.order_by(ValidationReport.created_at.desc())
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        reports = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return reports, total
    
    async def get_pending_for_validator(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ValidationReport], int]:
        """Get pending validation orders."""
        # This returns orders that need validation, not reports
        # Implementation depends on order filtering
        pass
    
    async def get_latest_by_order(self, order_id: UUID) -> Optional[ValidationReport]:
        """Get the latest validation report for an order."""
        result = await self.db.execute(
            select(ValidationReport)
            .where(ValidationReport.order_id == order_id)
            .order_by(ValidationReport.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()





