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
    
    async def get_payment_card(self) -> Optional[Dict[str, Any]]:
        """Get payment card info for card-to-card payments."""
        client = await self._get_client()
        try:
            response = await client.get("/api/v1/settings/payment-card")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error getting payment card: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"Error getting payment card: {e}")
            return None
    
    async def upload_receipt(
        self,
        payment_id: str,
        user_id: str,
        receipt_image_url: str,
    ) -> Optional[Dict[str, Any]]:
        """Upload receipt for card-to-card payment."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/payments/{payment_id}/upload-receipt",
                json={"receipt_image_url": receipt_image_url},
                params={"user_id": user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error uploading receipt: {e}")
            return None
    
    async def get_pending_approval_payments(
        self,
        admin_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Optional[Dict[str, Any]]:
        """Get payments pending approval (admin only)."""
        client = await self._get_client()
        try:
            response = await client.get(
                "/api/v1/payments/pending-approval",
                params={"admin_id": admin_id, "page": page, "page_size": page_size}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting pending payments: {e}")
            return None
    
    async def approve_payment(
        self,
        payment_id: str,
        admin_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Approve a payment (admin only)."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/payments/{payment_id}/approve",
                json={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error approving payment: {e}")
            return None
    
    async def reject_payment(
        self,
        payment_id: str,
        admin_id: str,
        reason: str,
    ) -> Optional[Dict[str, Any]]:
        """Reject a payment (admin only)."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/payments/{payment_id}/reject",
                json={"admin_id": admin_id, "reason": reason}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error rejecting payment: {e}")
            return None
    
    async def update_payment_card(
        self,
        admin_id: str,
        card_number: str | None = None,
        card_holder: str | None = None,
    ) -> Optional[Dict[str, Any]]:
        """Update payment card info (admin only). Partial update supported."""
        client = await self._get_client()
        try:
            # Build payload with only non-None values
            payload = {}
            if card_number is not None:
                payload["card_number"] = card_number
            if card_holder is not None:
                payload["card_holder"] = card_holder
            
            response = await client.patch(
                "/api/v1/settings/payment-card",
                json=payload,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error updating payment card: {e}")
            return None
    
    async def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment by ID."""
        client = await self._get_client()
        try:
            response = await client.get(f"/api/v1/payments/{payment_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting payment: {e}")
            return None
    
    # ==================== Admin Management APIs ====================
    
    async def get_all_admins(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """Get all admin users."""
        client = await self._get_client()
        try:
            response = await client.get(
                "/api/v1/users/admins/list",
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting admins: {e}")
            return None
    
    async def get_admin_telegram_ids(self) -> Optional[List[int]]:
        """Get telegram IDs of all active admins."""
        client = await self._get_client()
        try:
            response = await client.get("/api/v1/users/admins/telegram-ids")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting admin telegram IDs: {e}")
            return None
    
    async def promote_to_admin(
        self,
        target_telegram_id: int,
        admin_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Promote a user to admin."""
        client = await self._get_client()
        try:
            response = await client.post(
                "/api/v1/users/admins/promote",
                json={"target_telegram_id": target_telegram_id},
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error promoting user: {e}")
            return None
    
    async def demote_from_admin(
        self,
        target_telegram_id: int,
        admin_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Demote an admin to customer."""
        client = await self._get_client()
        try:
            response = await client.post(
                "/api/v1/users/admins/demote",
                json={"target_telegram_id": target_telegram_id},
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error demoting admin: {e}")
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
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by telegram ID - wrapper around get_user."""
        return await self.get_user(telegram_id)
    
    async def promote_to_admin(self, user_id: str, admin_id: str = None) -> Optional[Dict[str, Any]]:
        """Promote a user to admin (self-promotion for secret code)."""
        client = await self._get_client()
        try:
            # If admin_id is not provided, use user_id (self-promotion via secret code)
            params = {"admin_id": admin_id if admin_id else user_id}
            response = await client.post(
                f"/api/v1/users/{user_id}/promote",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error promoting user: {e}")
            return None
    
    # ==================== Category APIs ====================
    
    async def get_categories(self, active_only: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Get all categories."""
        client = await self._get_client()
        try:
            response = await client.get(
                "/api/v1/categories",
                params={"active_only": active_only}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting categories: {e}")
            return None
    
    async def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get category by ID."""
        client = await self._get_client()
        try:
            response = await client.get(f"/api/v1/categories/{category_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting category: {e}")
            return None
    
    async def get_category_details(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get category with all related data."""
        client = await self._get_client()
        try:
            response = await client.get(f"/api/v1/categories/{category_id}/details")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting category details: {e}")
            return None
    
    async def create_category(self, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new category."""
        client = await self._get_client()
        try:
            response = await client.post(
                "/api/v1/categories",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating category: {e}")
            return None
    
    async def update_category(self, category_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a category."""
        client = await self._get_client()
        try:
            response = await client.patch(
                f"/api/v1/categories/{category_id}",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error updating category: {e}")
            return None
    
    async def delete_category(self, category_id: str, admin_id: str) -> bool:
        """Delete a category."""
        client = await self._get_client()
        try:
            response = await client.delete(
                f"/api/v1/categories/{category_id}",
                params={"admin_id": admin_id}
            )
            return response.status_code == 204
        except httpx.HTTPError as e:
            logger.error(f"Error deleting category: {e}")
            return False
    
    # ==================== Attribute APIs ====================
    
    async def get_attributes(self, category_id: str, active_only: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Get all attributes for a category."""
        client = await self._get_client()
        try:
            response = await client.get(
                f"/api/v1/categories/{category_id}/attributes",
                params={"active_only": active_only}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting attributes: {e}")
            return None
    
    async def create_attribute(self, category_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new attribute."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/categories/{category_id}/attributes",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating attribute: {e}")
            return None
    
    async def update_attribute(self, attribute_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an attribute."""
        client = await self._get_client()
        try:
            response = await client.patch(
                f"/api/v1/attributes/{attribute_id}",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error updating attribute: {e}")
            return None
    
    async def delete_attribute(self, attribute_id: str, admin_id: str) -> bool:
        """Delete an attribute."""
        client = await self._get_client()
        try:
            response = await client.delete(
                f"/api/v1/attributes/{attribute_id}",
                params={"admin_id": admin_id}
            )
            return response.status_code == 204
        except httpx.HTTPError as e:
            logger.error(f"Error deleting attribute: {e}")
            return False
    
    async def create_attribute_option(self, attribute_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new attribute option."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/attributes/{attribute_id}/options",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating attribute option: {e}")
            return None
    
    async def delete_attribute_option(self, option_id: str, admin_id: str) -> bool:
        """Delete an attribute option."""
        client = await self._get_client()
        try:
            response = await client.delete(
                f"/api/v1/options/{option_id}",
                params={"admin_id": admin_id}
            )
            return response.status_code == 204
        except httpx.HTTPError as e:
            logger.error(f"Error deleting attribute option: {e}")
            return False
    
    # ==================== Design Plan APIs ====================
    
    async def get_design_plans(self, category_id: str, active_only: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Get all design plans for a category."""
        client = await self._get_client()
        try:
            response = await client.get(
                f"/api/v1/categories/{category_id}/plans",
                params={"active_only": active_only}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting design plans: {e}")
            return None
    
    async def get_design_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get design plan by ID."""
        client = await self._get_client()
        try:
            response = await client.get(f"/api/v1/plans/{plan_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting design plan: {e}")
            return None
    
    async def get_design_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get design plan with questions and templates."""
        client = await self._get_client()
        try:
            response = await client.get(f"/api/v1/plans/{plan_id}/details")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting design plan details: {e}")
            return None
    
    async def create_design_plan(self, category_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new design plan."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/categories/{category_id}/plans",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating design plan: {e}")
            return None
    
    async def update_design_plan(self, plan_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a design plan."""
        client = await self._get_client()
        try:
            response = await client.patch(
                f"/api/v1/plans/{plan_id}",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error updating design plan: {e}")
            return None
    
    async def delete_design_plan(self, plan_id: str, admin_id: str) -> bool:
        """Delete a design plan."""
        client = await self._get_client()
        try:
            response = await client.delete(
                f"/api/v1/plans/{plan_id}",
                params={"admin_id": admin_id}
            )
            return response.status_code == 204
        except httpx.HTTPError as e:
            logger.error(f"Error deleting design plan: {e}")
            return False
    
    # ==================== Question APIs ====================
    
    async def get_questions(self, plan_id: str, active_only: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Get all questions for a plan."""
        client = await self._get_client()
        try:
            response = await client.get(
                f"/api/v1/plans/{plan_id}/questions",
                params={"active_only": active_only}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting questions: {e}")
            return None
    
    async def create_question(self, plan_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new question."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/plans/{plan_id}/questions",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating question: {e}")
            return None
    
    async def update_question(self, question_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a question."""
        client = await self._get_client()
        try:
            response = await client.patch(
                f"/api/v1/questions/{question_id}",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error updating question: {e}")
            return None
    
    async def delete_question(self, question_id: str, admin_id: str) -> bool:
        """Delete a question."""
        client = await self._get_client()
        try:
            response = await client.delete(
                f"/api/v1/questions/{question_id}",
                params={"admin_id": admin_id}
            )
            return response.status_code == 204
        except httpx.HTTPError as e:
            logger.error(f"Error deleting question: {e}")
            return False
    
    async def create_question_option(self, question_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new question option."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/questions/{question_id}/options",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating question option: {e}")
            return None
    
    # ==================== Template APIs ====================
    
    async def get_templates(self, plan_id: str, active_only: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Get all templates for a plan."""
        client = await self._get_client()
        try:
            response = await client.get(
                f"/api/v1/plans/{plan_id}/templates",
                params={"active_only": active_only}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting templates: {e}")
            return None
    
    async def create_template(self, plan_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new template."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/plans/{plan_id}/templates",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating template: {e}")
            return None
    
    async def update_template(self, template_id: str, admin_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a template."""
        client = await self._get_client()
        try:
            response = await client.patch(
                f"/api/v1/templates/{template_id}",
                json=data,
                params={"admin_id": admin_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error updating template: {e}")
            return None
    
    async def delete_template(self, template_id: str, admin_id: str) -> bool:
        """Delete a template."""
        client = await self._get_client()
        try:
            response = await client.delete(
                f"/api/v1/templates/{template_id}",
                params={"admin_id": admin_id}
            )
            return response.status_code == 204
        except httpx.HTTPError as e:
            logger.error(f"Error deleting template: {e}")
            return False
    
    async def apply_logo_to_template(self, template_id: str, logo_url: str) -> Optional[Dict[str, Any]]:
        """Apply a logo to a template and get preview/final URLs."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/api/v1/templates/{template_id}/apply-logo",
                json={"logo_file_url": logo_url}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error applying logo to template: {e}")
            return None


# Singleton instance for easy import
api_client = APIClient()
