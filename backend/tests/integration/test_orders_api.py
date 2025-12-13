"""Integration tests for Orders API."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestOrdersAPI:
    """Integration tests for /api/v1/orders endpoints."""
    
    @pytest.fixture
    async def setup_user_and_product(self, client: AsyncClient, sample_user_data, sample_product_data):
        """Create user and product for order tests."""
        # Create user
        user_response = await client.post("/api/v1/users", json=sample_user_data)
        user = user_response.json()
        
        # Create product
        product_response = await client.post("/api/v1/products", json=sample_product_data)
        product = product_response.json()
        
        return user, product
    
    @pytest.mark.asyncio
    async def test_create_order(self, client: AsyncClient, setup_user_and_product, sample_order_data):
        """Test POST /api/v1/orders - create new order."""
        user, product = await setup_user_and_product
        sample_order_data["product_id"] = product["id"]
        
        response = await client.post(
            "/api/v1/orders",
            json=sample_order_data,
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user["id"]
        assert data["product_id"] == product["id"]
        assert "total_price" in data
    
    @pytest.mark.asyncio
    async def test_get_orders(self, client: AsyncClient, setup_user_and_product, sample_order_data):
        """Test GET /api/v1/orders - list user orders."""
        user, product = await setup_user_and_product
        sample_order_data["product_id"] = product["id"]
        
        # Create order
        await client.post(
            "/api/v1/orders",
            json=sample_order_data,
            params={"user_id": user["id"]}
        )
        
        response = await client.get("/api/v1/orders", params={"user_id": user["id"]})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_order_by_id(self, client: AsyncClient, setup_user_and_product, sample_order_data):
        """Test GET /api/v1/orders/{order_id}."""
        user, product = await setup_user_and_product
        sample_order_data["product_id"] = product["id"]
        
        # Create order
        create_response = await client.post(
            "/api/v1/orders",
            json=sample_order_data,
            params={"user_id": user["id"]}
        )
        order_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/orders/{order_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
    
    @pytest.mark.asyncio
    async def test_cancel_order(self, client: AsyncClient, setup_user_and_product, sample_order_data):
        """Test POST /api/v1/orders/{order_id}/cancel."""
        user, product = await setup_user_and_product
        sample_order_data["product_id"] = product["id"]
        
        # Create order
        create_response = await client.post(
            "/api/v1/orders",
            json=sample_order_data,
            params={"user_id": user["id"]}
        )
        order_id = create_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/orders/{order_id}/cancel",
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CANCELLED"
    
    @pytest.mark.asyncio
    async def test_update_order_status(self, client: AsyncClient, setup_user_and_product, sample_order_data):
        """Test PATCH /api/v1/orders/{order_id}/status."""
        user, product = await setup_user_and_product
        sample_order_data["product_id"] = product["id"]
        
        # Create order
        create_response = await client.post(
            "/api/v1/orders",
            json=sample_order_data,
            params={"user_id": user["id"]}
        )
        order_id = create_response.json()["id"]
        
        # Update status
        response = await client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "READY_FOR_PRINT"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "READY_FOR_PRINT"
    
    @pytest.mark.asyncio
    async def test_printshop_queue(self, client: AsyncClient, setup_user_and_product, sample_order_data):
        """Test GET /api/v1/printshop/orders."""
        user, product = await setup_user_and_product
        sample_order_data["product_id"] = product["id"]
        
        # Create order and set to READY_FOR_PRINT
        create_response = await client.post(
            "/api/v1/orders",
            json=sample_order_data,
            params={"user_id": user["id"]}
        )
        order_id = create_response.json()["id"]
        
        await client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "READY_FOR_PRINT"}
        )
        
        response = await client.get("/api/v1/printshop/orders")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

