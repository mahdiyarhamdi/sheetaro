"""Validation schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional


class ValidationIssue(BaseModel):
    """Schema for a validation issue."""
    type: str = Field(..., description="Issue type (resolution, font, bleed, color, format)")
    severity: str = Field(..., description="Issue severity (low, medium, high, critical)")
    description: str = Field(..., description="Issue description")
    suggestion: Optional[str] = Field(None, description="Fix suggestion")


class ValidationRequestCreate(BaseModel):
    """Schema for requesting validation."""
    order_id: UUID = Field(..., description="Order ID")


class ValidationReportCreate(BaseModel):
    """Schema for creating a validation report."""
    order_id: UUID = Field(..., description="Order ID")
    issues: list[ValidationIssue] = Field(default_factory=list, description="List of issues found")
    fix_cost: Decimal = Field(default=0, ge=0, description="Suggested fix cost in Tomans")
    summary: Optional[str] = Field(None, description="Validation summary")
    passed: str = Field(..., description="Validation result (PASSED/FAILED)")


class ValidationReportOut(BaseModel):
    """Schema for validation report output."""
    id: UUID
    order_id: UUID
    validator_id: UUID
    issues: list[ValidationIssue]
    fix_cost: Decimal
    summary: Optional[str] = None
    passed: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ValidationReportListResponse(BaseModel):
    """Response schema for validation report list."""
    items: list[ValidationReportOut]
    total: int
    page: int
    page_size: int


class FixRequestCreate(BaseModel):
    """Schema for requesting a fix."""
    order_id: UUID = Field(..., description="Order ID")
    validation_report_id: UUID = Field(..., description="Validation report ID")
    accept_cost: bool = Field(..., description="Accept the fix cost")




