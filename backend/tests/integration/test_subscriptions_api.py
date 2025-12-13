"""Integration tests for Subscriptions API."""

import pytest
from httpx import AsyncClient


class TestSubscriptionsAPI:
    """Integration tests for /api/v1/subscriptions endpoints."""
    
    @pytest.fixture
    async def setup_user(self, client: AsyncClient, sample_user_data):
        """Create user for subscription tests."""
        user_response = await client.post("/api/v1/users", json=sample_user_data)
        return user_response.json()
    
    @pytest.mark.asyncio
    async def test_create_subscription(self, client: AsyncClient, setup_user):
        """Test POST /api/v1/subscriptions - create subscription."""
        user = await setup_user
        
        response = await client.post(
            "/api/v1/subscriptions",
            json={"plan": "ADVANCED_SEARCH"},
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["plan"] == "ADVANCED_SEARCH"
        assert data["price"] == 250000
        assert data["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_get_subscription_status(self, client: AsyncClient, setup_user):
        """Test GET /api/v1/subscriptions/me."""
        user = await setup_user
        
        # Without subscription
        response1 = await client.get(
            "/api/v1/subscriptions/me",
            params={"user_id": user["id"]}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["has_active_subscription"] is False
        
        # Create subscription
        await client.post(
            "/api/v1/subscriptions",
            json={"plan": "ADVANCED_SEARCH"},
            params={"user_id": user["id"]}
        )
        
        # With subscription
        response2 = await client.get(
            "/api/v1/subscriptions/me",
            params={"user_id": user["id"]}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["has_active_subscription"] is True
        assert data2["days_remaining"] == 30
    
    @pytest.mark.asyncio
    async def test_list_subscriptions(self, client: AsyncClient, setup_user):
        """Test GET /api/v1/subscriptions."""
        user = await setup_user
        
        # Create subscription
        await client.post(
            "/api/v1/subscriptions",
            json={"plan": "ADVANCED_SEARCH"},
            params={"user_id": user["id"]}
        )
        
        response = await client.get(
            "/api/v1/subscriptions",
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_cancel_subscription(self, client: AsyncClient, setup_user):
        """Test POST /api/v1/subscriptions/{subscription_id}/cancel."""
        user = await setup_user
        
        # Create subscription
        create_response = await client.post(
            "/api/v1/subscriptions",
            json={"plan": "ADVANCED_SEARCH"},
            params={"user_id": user["id"]}
        )
        subscription_id = create_response.json()["id"]
        
        # Cancel
        response = await client.post(
            f"/api/v1/subscriptions/{subscription_id}/cancel",
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    @pytest.mark.asyncio
    async def test_get_plan_price(self, client: AsyncClient):
        """Test GET /api/v1/subscriptions/plans/price."""
        response = await client.get(
            "/api/v1/subscriptions/plans/price",
            params={"plan": "ADVANCED_SEARCH"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["plan"] == "ADVANCED_SEARCH"
        assert data["price"] == 250000
        assert data["duration_days"] == 30

