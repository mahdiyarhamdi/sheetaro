"""Structured logging for Sheetaro application.

This module provides JSON-formatted logging with support for:
- Request context (IP, user agent)
- Event-based logging for auditing
- Error tracking with stack traces
"""

import logging
import json
from typing import Any, Optional
from datetime import datetime, timezone
from contextvars import ContextVar

# Context variables for request-scoped data
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
client_ip_var: ContextVar[Optional[str]] = ContextVar("client_ip", default=None)
user_agent_var: ContextVar[Optional[str]] = ContextVar("user_agent", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def set_request_context(
    request_id: Optional[str] = None,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """Set request context for logging."""
    if request_id:
        request_id_var.set(request_id)
    if client_ip:
        client_ip_var.set(client_ip)
    if user_agent:
        user_agent_var.set(user_agent)
    if user_id:
        user_id_var.set(user_id)


def clear_request_context() -> None:
    """Clear request context after request completes."""
    request_id_var.set(None)
    client_ip_var.set(None)
    user_agent_var.set(None)
    user_id_var.set(None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request context if available
        if request_id_var.get():
            log_data["request_id"] = request_id_var.get()
        if client_ip_var.get():
            log_data["client_ip"] = client_ip_var.get()
        if user_agent_var.get():
            log_data["user_agent"] = user_agent_var.get()
        if user_id_var.get():
            log_data["user_id"] = user_id_var.get()
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(name: str = "app", level: int = logging.INFO) -> logging.Logger:
    """Setup structured logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    
    return logger


logger = setup_logger()


def log_event(
    event_type: str,
    level: str = "INFO",
    **kwargs: Any,
) -> None:
    """
    Log an event with structured data.
    
    Args:
        event_type: Type of event (e.g., 'user.signup', 'order.create')
        level: Log level (INFO, WARNING, ERROR)
        **kwargs: Additional event data
    
    Required events per ARCHITECTURE.md:
        - user.signup: New user registration
        - user.login: User authenticated
        - user.update: Profile updated
        - user.promoted_to_admin: User became admin
        - user.demoted_from_admin: Admin reverted to customer
        - order.create: New order
        - order.status_change: Order status update
        - payment.initiated: Payment initiated
        - payment.receipt_uploaded: Receipt image uploaded
        - payment.approved: Payment approved by admin
        - payment.rejected: Payment rejected by admin
    """
    log_data = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    # Add request context
    if client_ip_var.get():
        log_data["ip"] = client_ip_var.get()
    if user_agent_var.get():
        log_data["ua"] = user_agent_var.get()
    if user_id_var.get():
        log_data["user_id"] = user_id_var.get()
    
    # Add event-specific data
    log_data.update(kwargs)
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(json.dumps(log_data, ensure_ascii=False))


# Convenience functions for common event types
def log_user_signup(
    telegram_id: int,
    user_id: str,
    username: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Log user signup event."""
    log_event(
        event_type="user.signup",
        telegram_id=telegram_id,
        user_id=user_id,
        username=username,
        **kwargs,
    )


def log_user_login(
    telegram_id: int,
    user_id: str,
    **kwargs: Any,
) -> None:
    """Log user login event."""
    log_event(
        event_type="user.login",
        telegram_id=telegram_id,
        user_id=user_id,
        **kwargs,
    )


def log_order_create(
    order_id: str,
    user_id: str,
    product_id: str,
    design_plan: str,
    total_price: str,
    **kwargs: Any,
) -> None:
    """Log order creation event."""
    log_event(
        event_type="order.create",
        order_id=order_id,
        user_id=user_id,
        product_id=product_id,
        design_plan=design_plan,
        total_price=total_price,
        **kwargs,
    )


def log_order_status_change(
    order_id: str,
    old_status: Optional[str],
    new_status: str,
    **kwargs: Any,
) -> None:
    """Log order status change event."""
    log_event(
        event_type="order.status_change",
        order_id=order_id,
        old_status=old_status,
        new_status=new_status,
        **kwargs,
    )


def log_payment_initiated(
    payment_id: str,
    order_id: str,
    amount: str,
    payment_type: str,
    **kwargs: Any,
) -> None:
    """Log payment initiation event."""
    log_event(
        event_type="payment.initiated",
        payment_id=payment_id,
        order_id=order_id,
        amount=amount,
        payment_type=payment_type,
        **kwargs,
    )


def log_receipt_uploaded(
    payment_id: str,
    user_id: str,
    receipt_url: str,
    **kwargs: Any,
) -> None:
    """Log receipt upload event."""
    log_event(
        event_type="payment.receipt_uploaded",
        payment_id=payment_id,
        user_id=user_id,
        receipt_url=receipt_url,
        **kwargs,
    )


def log_payment_approved(
    payment_id: str,
    admin_id: str,
    **kwargs: Any,
) -> None:
    """Log payment approval event."""
    log_event(
        event_type="payment.approved",
        payment_id=payment_id,
        admin_id=admin_id,
        outcome="approved",
        **kwargs,
    )


def log_payment_rejected(
    payment_id: str,
    admin_id: str,
    reason: str,
    **kwargs: Any,
) -> None:
    """Log payment rejection event."""
    log_event(
        event_type="payment.rejected",
        payment_id=payment_id,
        admin_id=admin_id,
        reason=reason,
        outcome="rejected",
        **kwargs,
    )


def log_admin_action(
    action: str,
    admin_id: str,
    target_id: str,
    target_type: str,
    **kwargs: Any,
) -> None:
    """Log admin action event."""
    log_event(
        event_type=f"admin.{action}",
        admin_id=admin_id,
        target_id=target_id,
        target_type=target_type,
        **kwargs,
    )


def log_error(
    error_type: str,
    message: str,
    **kwargs: Any,
) -> None:
    """Log error event."""
    log_event(
        event_type=f"error.{error_type}",
        level="ERROR",
        message=message,
        **kwargs,
    )

