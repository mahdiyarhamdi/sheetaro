from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.api.routers import health, users, products, orders, payments, validation, invoices, subscriptions, files
from app.api.routers import settings as settings_router
from app.api.routers.categories import (
    router as categories_router,
    attributes_router,
    options_router,
    plans_router,
    sections_router,
    questions_router,
    question_options_router,
    templates_router,
    step_templates_router,
    processed_designs_router,
    answers_router,
)
from app.utils.logger import logger, set_request_context, clear_request_context


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for Sheetaro Telegram Print Bot - سفارش لیبل و کارت ویزیت",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request context middleware for logging
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Middleware to set request context for logging."""
    import uuid
    
    # Generate request ID
    request_id = str(uuid.uuid4())[:8]
    
    # Get client IP (handle proxy headers)
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.headers.get("X-Real-IP", "")
    if not client_ip and request.client:
        client_ip = request.client.host
    
    # Get user agent
    user_agent = request.headers.get("User-Agent", "")
    
    # Get user_id from query params if available
    user_id = request.query_params.get("user_id", "")
    
    # Set context for logging
    set_request_context(
        request_id=request_id,
        client_ip=client_ip,
        user_agent=user_agent[:200] if user_agent else None,  # Truncate long user agents
        user_id=user_id if user_id else None,
    )
    
    try:
        response = await call_next(request)
        return response
    finally:
        clear_request_context()


# Import custom exceptions
from app.exceptions import (
    SheetaroException,
    BusinessException,
    ResourceNotFoundException,
    AuthorizationException,
    PermissionDeniedException,
    AdminRequiredException,
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    # Convert errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        err_dict = dict(error)
        # Convert any non-serializable ctx values to strings
        if 'ctx' in err_dict and isinstance(err_dict['ctx'], dict):
            for key, value in err_dict['ctx'].items():
                if isinstance(value, Exception):
                    err_dict['ctx'][key] = str(value)
        errors.append(err_dict)
    logger.error(f"Validation error: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )


@app.exception_handler(ResourceNotFoundException)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException) -> JSONResponse:
    """Handle resource not found errors."""
    logger.warning(f"Resource not found: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=exc.to_dict(),
    )


@app.exception_handler(AdminRequiredException)
async def admin_required_handler(request: Request, exc: AdminRequiredException) -> JSONResponse:
    """Handle admin required errors."""
    logger.warning(f"Admin access denied: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=exc.to_dict(),
    )


@app.exception_handler(PermissionDeniedException)
async def permission_denied_handler(request: Request, exc: PermissionDeniedException) -> JSONResponse:
    """Handle permission denied errors."""
    logger.warning(f"Permission denied: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=exc.to_dict(),
    )


@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(request: Request, exc: AuthorizationException) -> JSONResponse:
    """Handle authorization errors."""
    logger.warning(f"Authorization error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=exc.to_dict(),
    )


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
    """Handle business logic errors."""
    logger.warning(f"Business error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.to_dict(),
    )


@app.exception_handler(SheetaroException)
async def sheetaro_exception_handler(request: Request, exc: SheetaroException) -> JSONResponse:
    """Handle base Sheetaro errors."""
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.to_dict(),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors."""
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "DATABASE_ERROR", "message": "Database error occurred", "details": {}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "INTERNAL_ERROR", "message": "Internal server error", "details": {}},
    )


# Health check router
app.include_router(health.router, tags=["Health"])

# API v1 routers
app.include_router(
    users.router,
    prefix="/api/v1",
    tags=["Users"]
)

app.include_router(
    products.router,
    prefix="/api/v1",
    tags=["Products"]
)

app.include_router(
    orders.router,
    prefix="/api/v1",
    tags=["Orders"]
)

app.include_router(
    payments.router,
    prefix="/api/v1",
    tags=["Payments"]
)

app.include_router(
    validation.router,
    prefix="/api/v1",
    tags=["Validation"]
)

app.include_router(
    invoices.router,
    prefix="/api/v1",
    tags=["Invoices"]
)

app.include_router(
    subscriptions.router,
    prefix="/api/v1",
    tags=["Subscriptions"]
)

app.include_router(
    files.router,
    prefix="/api/v1",
    tags=["Files"]
)

app.include_router(
    settings_router.router,
    prefix="/api/v1",
    tags=["Settings"]
)

# Dynamic categories routers
app.include_router(categories_router, tags=["Categories"])
app.include_router(attributes_router, tags=["Attributes"])
app.include_router(options_router, tags=["Options"])
app.include_router(plans_router, tags=["Plans"])
app.include_router(sections_router, tags=["Sections"])
app.include_router(questions_router, tags=["Questions"])
app.include_router(question_options_router, tags=["Question Options"])
app.include_router(templates_router, tags=["Templates"])
app.include_router(step_templates_router, tags=["Step Templates"])
app.include_router(processed_designs_router, tags=["Processed Designs"])
app.include_router(answers_router, tags=["Answers"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)

