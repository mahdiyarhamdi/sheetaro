import httpx
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with backend API."""
    
    _instance: Optional["APIClient"] = None
    _client: Optional[httpx.AsyncClient] = None
    
    def __new__(cls) -> "APIClient":
        """Singleton pattern to reuse the same client instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.base_url = os.getenv("API_BASE_URL", "http://backend:3001")
            self.timeout = httpx.Timeout(30.0, connect=10.0)
            self._initialized = True
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def create_or_update_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create or update user in backend."""
        client = await self._get_client()
        try:
            response = await client.post("/api/v1/users", json=user_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating/updating user: {e}")
            return None
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by telegram ID."""
        client = await self._get_client()
        try:
            response = await client.get(f"/api/v1/users/{telegram_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error getting user: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def update_user(self, telegram_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user by telegram ID."""
        client = await self._get_client()
        try:
            response = await client.patch(f"/api/v1/users/{telegram_id}", json=user_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error updating user: {e}")
            return None


# Singleton instance for easy import
api_client = APIClient()

