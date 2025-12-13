"""API client for communicating with backend."""

import httpx
import os
import logging
from typing import Optional, Dict, Any, List

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
    
    # ==================== User APIs ====================
    
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
    
    # ==================== Product APIs ====================
    
    async def get_products(
        self,
        product_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Optional[Dict[str, Any]]:
        """Get list of products."""
        client = await self._get_client()
        try:
            params = {"page": page, "page_size": page_size}
            if product_type:
                params["type"] = product_type
            response = await client.get("/api/v1/products", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting products: {e}")
            return None
    
    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        client = await self._get_client()
        try:
            response = await client.get(f"/api/v1/products/{product_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting product: {e}")
            return None
    
    # ==================== Order APIs ====================
    
    async def create_order(self, user_id: str, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new order."""
        client = await self._get_client()
        try:
            response = await client.post(
                "/api/v1/orders",
                json=order_data,
                params={"user_id": user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    async def get_user_orders(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Optional[Dict[str, Any]]:
        """Get orders for a user."""
        client = await self._get_client()
        try:
            params = {"user_id": user_id, "page": page, "page_size": page_size}
            if status:
                params["status"] = status
            response = await client.get("/api/v1/orders", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting orders: {e}")
            return None
    
    async def get_order(self, order_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get order by ID."""
        client = await self._get_client()
        try:
            params = {}
            if user_id:
                params["user_id"] = user_id
            response = await client.get(f"/api/v1/orders/{order_id}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting order: {e}")
            return None
    
    async def cancel_order(self, order_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Cancel an order."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/orders/{order_id}/cancel",
                params={"user_id": user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error cancelling order: {e}")
            return None
    
    # ==================== Payment APIs ====================
    
    async def initiate_payment(
        self,
        user_id: str,
        order_id: str,
        payment_type: str,
        callback_url: str,
    ) -> Optional[Dict[str, Any]]:
        """Initiate a payment."""
        client = await self._get_client()
        try:
            response = await client.post(
                "/api/v1/payments/initiate",
                json={
                    "order_id": order_id,
                    "type": payment_type,
                    "callback_url": callback_url,
                },
                params={"user_id": user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error initiating payment: {e}")
            return None
    
    async def get_payment_summary(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get payment summary for an order."""
        client = await self._get_client()
        try:
            response = await client.get(f"/api/v1/payments/order/{order_id}/summary")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting payment summary: {e}")
            return None
    
    # ==================== Subscription APIs ====================
    
    async def get_subscription_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription status for a user."""
        client = await self._get_client()
        try:
            response = await client.get(
                "/api/v1/subscriptions/me",
                params={"user_id": user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting subscription status: {e}")
            return None


# Singleton instance for easy import
api_client = APIClient()
