"""Custom exceptions for Sheetaro application.

This module provides a hierarchy of exceptions for standardized error handling
across the application.
"""

from typing import Optional, Dict, Any


class SheetaroException(Exception):
    """Base exception for all Sheetaro application errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


# ==================== Business Logic Exceptions ====================

class BusinessException(SheetaroException):
    """Base exception for business logic errors (400 Bad Request)."""
    pass


class ResourceNotFoundException(SheetaroException):
    """Resource not found (404 Not Found)."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        message: Optional[str] = None,
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message=message or f"{resource_type} with id {resource_id} not found",
            code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": str(resource_id)},
        )


class ValidationException(BusinessException):
    """Validation error (400 Bad Request)."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details,
        )


class InvalidStateException(BusinessException):
    """Invalid state transition (400 Bad Request)."""
    
    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        expected_states: Optional[list] = None,
    ):
        details = {}
        if current_state:
            details["current_state"] = current_state
        if expected_states:
            details["expected_states"] = expected_states
        
        super().__init__(
            message=message,
            code="INVALID_STATE",
            details=details,
        )


class DuplicateResourceException(BusinessException):
    """Duplicate resource error (409 Conflict)."""
    
    def __init__(
        self,
        resource_type: str,
        identifier: str,
        message: Optional[str] = None,
    ):
        super().__init__(
            message=message or f"{resource_type} with {identifier} already exists",
            code="DUPLICATE_RESOURCE",
            details={"resource_type": resource_type, "identifier": identifier},
        )


# ==================== Authorization Exceptions ====================

class AuthorizationException(SheetaroException):
    """Base exception for authorization errors (403 Forbidden)."""
    pass


class PermissionDeniedException(AuthorizationException):
    """Permission denied (403 Forbidden)."""
    
    def __init__(
        self,
        required_permission: Optional[str] = None,
        message: Optional[str] = None,
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        
        super().__init__(
            message=message or "Permission denied",
            code="PERMISSION_DENIED",
            details=details,
        )


class AdminRequiredException(AuthorizationException):
    """Admin access required (403 Forbidden)."""
    
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            message=message or "Admin access required",
            code="ADMIN_REQUIRED",
        )


class OwnershipRequiredException(AuthorizationException):
    """Resource ownership required (403 Forbidden)."""
    
    def __init__(
        self,
        resource_type: str,
        message: Optional[str] = None,
    ):
        super().__init__(
            message=message or f"You do not own this {resource_type}",
            code="OWNERSHIP_REQUIRED",
            details={"resource_type": resource_type},
        )


# ==================== Payment Exceptions ====================

class PaymentException(BusinessException):
    """Base exception for payment errors."""
    pass


class PaymentNotFoundError(PaymentException, ResourceNotFoundException):
    """Payment not found."""
    
    def __init__(self, payment_id: Any):
        ResourceNotFoundException.__init__(
            self,
            resource_type="Payment",
            resource_id=payment_id,
        )


class InvalidPaymentStateError(PaymentException, InvalidStateException):
    """Invalid payment state for operation."""
    
    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
    ):
        InvalidStateException.__init__(
            self,
            message=message,
            current_state=current_state,
        )


class PaymentAlreadyProcessedError(PaymentException):
    """Payment has already been processed."""
    
    def __init__(self, payment_id: Any):
        super().__init__(
            message="Payment has already been processed",
            code="PAYMENT_ALREADY_PROCESSED",
            details={"payment_id": str(payment_id)},
        )


# ==================== Order Exceptions ====================

class OrderException(BusinessException):
    """Base exception for order errors."""
    pass


class OrderNotFoundError(OrderException, ResourceNotFoundException):
    """Order not found."""
    
    def __init__(self, order_id: Any):
        ResourceNotFoundException.__init__(
            self,
            resource_type="Order",
            resource_id=order_id,
        )


class InvalidOrderStateError(OrderException, InvalidStateException):
    """Invalid order state for operation."""
    
    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
    ):
        InvalidStateException.__init__(
            self,
            message=message,
            current_state=current_state,
        )


class OrderCannotBeCancelledError(OrderException):
    """Order cannot be cancelled in current state."""
    
    def __init__(self, order_id: Any, current_state: str):
        super().__init__(
            message=f"Cannot cancel order in state {current_state}",
            code="ORDER_CANNOT_BE_CANCELLED",
            details={"order_id": str(order_id), "current_state": current_state},
        )


# ==================== User Exceptions ====================

class UserException(BusinessException):
    """Base exception for user errors."""
    pass


class UserNotFoundError(UserException, ResourceNotFoundException):
    """User not found."""
    
    def __init__(self, identifier: Any, by_field: str = "id"):
        ResourceNotFoundException.__init__(
            self,
            resource_type="User",
            resource_id=identifier,
            message=f"User with {by_field} {identifier} not found",
        )


class UserAlreadyAdminError(UserException):
    """User is already an admin."""
    
    def __init__(self, telegram_id: int):
        super().__init__(
            message="User is already an admin",
            code="USER_ALREADY_ADMIN",
            details={"telegram_id": telegram_id},
        )


class LastAdminError(UserException):
    """Cannot remove the last admin."""
    
    def __init__(self):
        super().__init__(
            message="Cannot remove the last admin",
            code="LAST_ADMIN_ERROR",
        )


# ==================== File Exceptions ====================

class FileException(BusinessException):
    """Base exception for file errors."""
    pass


class FileTooLargeError(FileException):
    """File size exceeds maximum limit."""
    
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)",
            code="FILE_TOO_LARGE",
            details={"file_size": file_size, "max_size": max_size},
        )


class InvalidFileTypeError(FileException):
    """Invalid file type."""
    
    def __init__(self, content_type: str, allowed_types: list):
        super().__init__(
            message=f"Invalid file type: {content_type}",
            code="INVALID_FILE_TYPE",
            details={"content_type": content_type, "allowed_types": allowed_types},
        )


class FileNotFoundError(FileException, ResourceNotFoundException):
    """File not found."""
    
    def __init__(self, file_path: str):
        ResourceNotFoundException.__init__(
            self,
            resource_type="File",
            resource_id=file_path,
        )

