import httpx
import os
from typing import Optional, Dict, Any


class APIClient:
    """Client for communicating with backend API."""
    
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://backend:3001")
        self.timeout = 30.0
    
    async def create_or_update_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create or update user in backend."""
        url = f"{self.base_url}/api/v1/users"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=user_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error creating/updating user: {e}")
                return None
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by telegram ID."""
        url = f"{self.base_url}/api/v1/users/{telegram_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                print(f"Error getting user: {e}")
                return None
            except httpx.HTTPError as e:
                print(f"Error getting user: {e}")
                return None
    
    async def update_user(self, telegram_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user by telegram ID."""
        url = f"{self.base_url}/api/v1/users/{telegram_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.patch(url, json=user_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error updating user: {e}")
                return None

