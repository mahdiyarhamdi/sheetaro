"""Database configuration and session management.

This module provides the database engine, session factory, and dependency injection
for database sessions following best practices for transaction management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from app.core.config import settings


# Create async engine with connection pool
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency for FastAPI routes.
    
    This dependency provides a database session that automatically commits
    on success or rolls back on failure. The session is closed after the
    request completes.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use db session
            pass
    
    Note: For complex transactions spanning multiple operations, consider using
    the transaction context manager directly in your service layer.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session context manager for use outside of FastAPI routes.
    
    This is useful for background tasks, migrations, or testing where
    you need more control over the session lifecycle.
    
    Usage:
        async with get_db_context() as db:
            # Use db session
            await db.commit()  # Explicit commit required
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


class UnitOfWork:
    """
    Unit of Work pattern for managing transactions.
    
    Provides explicit control over transaction boundaries for complex
    operations that span multiple repository calls.
    
    Usage:
        async with UnitOfWork() as uow:
            user_repo = UserRepository(uow.session)
            order_repo = OrderRepository(uow.session)
            
            user = await user_repo.create(user_data)
            order = await order_repo.create(order_data)
            
            await uow.commit()  # Both operations committed together
    """
    
    def __init__(self):
        self.session: AsyncSession | None = None
    
    async def __aenter__(self) -> "UnitOfWork":
        self.session = AsyncSessionLocal()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        if self.session:
            await self.session.close()
    
    async def commit(self):
        """Commit the current transaction."""
        if self.session:
            await self.session.commit()
    
    async def rollback(self):
        """Rollback the current transaction."""
        if self.session:
            await self.session.rollback()
    
    async def flush(self):
        """Flush pending changes without committing."""
        if self.session:
            await self.session.flush()

