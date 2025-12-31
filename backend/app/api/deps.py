"""API dependencies."""
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status

from app.core.database import get_db


async def get_current_admin_user(x_admin_id: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Get current admin user from header.
    For now, this is a simple check - in production, implement proper auth.
    """
    # For development/MVP, we allow any request with admin_id header
    # In production, this should validate JWT token or session
    if not x_admin_id:
        # Allow without auth for now (MVP mode)
        return {"id": "system", "role": "ADMIN"}
    return {"id": x_admin_id, "role": "ADMIN"}


# Re-export get_db from database module to maintain backwards compatibility
# and provide a single source of truth for the dependency
__all__ = ["get_db", "get_current_admin_user"]

