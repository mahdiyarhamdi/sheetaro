"""API dependencies."""
from app.core.database import get_db

# Re-export get_db from database module to maintain backwards compatibility
# and provide a single source of truth for the dependency
__all__ = ["get_db"]

