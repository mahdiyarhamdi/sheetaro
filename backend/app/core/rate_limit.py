"""Rate limiting configuration using slowapi with Redis backend."""

from typing import Callable, Optional
from fastapi import Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


def get_user_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses user_id from query params if available, otherwise IP address.
    """
    # Try to get user_id from query params
    user_id = request.query_params.get("user_id")
    if user_id:
        return f"user:{user_id}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Initialize limiter with Redis storage
# Falls back to in-memory if Redis is not available
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["1000/hour"],  # Default limit for all endpoints
    storage_uri=settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else None,
    strategy="fixed-window",
)


# Rate limit presets for different endpoint types
class RateLimits:
    """Predefined rate limit configurations."""
    
    # Authentication related
    LOGIN = "5/minute"
    REGISTER = "10/minute"
    MAKE_ADMIN = "3/hour"
    
    # Payment related (sensitive)
    PAYMENT_INITIATE = "10/minute"
    PAYMENT_CALLBACK = "30/minute"
    RECEIPT_UPLOAD = "5/minute"
    PAYMENT_APPROVE = "30/minute"
    
    # File uploads
    FILE_UPLOAD = "20/minute"
    
    # General API
    READ = "100/minute"
    WRITE = "30/minute"
    LIST = "60/minute"
    
    # Admin operations
    ADMIN_READ = "60/minute"
    ADMIN_WRITE = "30/minute"
    
    # Message/notification
    MESSAGE_SEND = "20/minute"


async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "درخواست‌های شما بیش از حد مجاز است. لطفاً کمی صبر کنید.",
            "error": "rate_limit_exceeded",
            "retry_after": exc.detail,
        },
        headers={"Retry-After": str(exc.detail)},
    )


def get_limiter() -> Limiter:
    """Get the configured rate limiter instance."""
    return limiter


# Decorator shortcuts for common rate limits
def limit_login(func: Callable) -> Callable:
    """Rate limit decorator for login endpoints."""
    return limiter.limit(RateLimits.LOGIN)(func)


def limit_register(func: Callable) -> Callable:
    """Rate limit decorator for registration endpoints."""
    return limiter.limit(RateLimits.REGISTER)(func)


def limit_payment(func: Callable) -> Callable:
    """Rate limit decorator for payment initiation."""
    return limiter.limit(RateLimits.PAYMENT_INITIATE)(func)


def limit_upload(func: Callable) -> Callable:
    """Rate limit decorator for file uploads."""
    return limiter.limit(RateLimits.FILE_UPLOAD)(func)


def limit_read(func: Callable) -> Callable:
    """Rate limit decorator for read operations."""
    return limiter.limit(RateLimits.READ)(func)


def limit_write(func: Callable) -> Callable:
    """Rate limit decorator for write operations."""
    return limiter.limit(RateLimits.WRITE)(func)


def limit_admin(func: Callable) -> Callable:
    """Rate limit decorator for admin operations."""
    return limiter.limit(RateLimits.ADMIN_WRITE)(func)

