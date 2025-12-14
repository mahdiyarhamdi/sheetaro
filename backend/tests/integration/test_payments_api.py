"""Integration tests for Payments API."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestPaymentsAPI:
    """Integration tests for /api/v1/payments endpoints."""
    
    @pytest.fixture
    async def setup_order(self, client: AsyncClient, sample_user_data, sample_product_data, sample_order_data):
        """Create user, product, and order for payment tests."""
        # Create user
        user_response = await client.post("/api/v1/users", json=sample_user_data)
        user = user_response.json()
        
        # Create product
        product_response = await client.post("/api/v1/products", json=sample_product_data)
        product = product_response.json()
        
        # Create order
        sample_order_data["product_id"] = product["id"]
        order_response = await client.post(
            "/api/v1/orders",
            json=sample_order_data,
            params={"user_id": user["id"]}
        )
        order = order_response.json()
        
        return user, product, order
    
    @pytest.mark.asyncio
    async def test_initiate_payment(self, client: AsyncClient, setup_order):
        """Test POST /api/v1/payments/initiate."""
        user, product, order = await setup_order
        
        payment_data = {
            "order_id": order["id"],
            "type": "PRINT",
            "callback_url": "https://example.com/callback",
        }
        
        response = await client.post(
            "/api/v1/payments/initiate",
            json=payment_data,
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "payment_id" in data
        assert "authority" in data
        assert "redirect_url" in data
        assert data["amount"] == order["print_price"]
    
    @pytest.mark.asyncio
    async def test_payment_callback_success(self, client: AsyncClient, setup_order):
        """Test POST /api/v1/payments/callback - success."""
        user, product, order = await setup_order
        
        # Initiate payment
        payment_data = {
            "order_id": order["id"],
            "type": "PRINT",
            "callback_url": "https://example.com/callback",
        }
        init_response = await client.post(
            "/api/v1/payments/initiate",
            json=payment_data,
            params={"user_id": user["id"]}
        )
        authority = init_response.json()["authority"]
        
        # Handle callback
        callback_data = {
            "authority": authority,
            "status": "OK",
            "ref_id": "REF123456",
        }
        
        response = await client.post("/api/v1/payments/callback", json=callback_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["ref_id"] == "REF123456"
    
    @pytest.mark.asyncio
    async def test_get_order_payments(self, client: AsyncClient, setup_order):
        """Test GET /api/v1/payments/order/{order_id}."""
        user, product, order = await setup_order
        
        # Initiate payment
        payment_data = {
            "order_id": order["id"],
            "type": "PRINT",
            "callback_url": "https://example.com/callback",
        }
        await client.post(
            "/api/v1/payments/initiate",
            json=payment_data,
            params={"user_id": user["id"]}
        )
        
        response = await client.get(f"/api/v1/payments/order/{order['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_payment_summary(self, client: AsyncClient, setup_order):
        """Test GET /api/v1/payments/order/{order_id}/summary."""
        user, product, order = await setup_order
        
        response = await client.get(f"/api/v1/payments/order/{order['id']}/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_paid" in data
        assert "total_pending" in data
        assert "payments" in data


class TestCardToCardPaymentsAPI:
    """Integration tests for card-to-card payment endpoints."""
    
    @pytest.fixture
    async def setup_admin(self, client: AsyncClient):
        """Create an admin user."""
        admin_data = {
            "telegram_id": 888888888,
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "role": "ADMIN",
        }
        response = await client.post("/api/v1/users", json=admin_data)
        return response.json()
    
    @pytest.fixture
    async def setup_order_with_payment(self, client: AsyncClient, sample_user_data, sample_product_data, sample_order_data):
        """Create user, product, order, and initiated payment."""
        # Create user
        user_response = await client.post("/api/v1/users", json=sample_user_data)
        user = user_response.json()
        
        # Create product
        product_response = await client.post("/api/v1/products", json=sample_product_data)
        product = product_response.json()
        
        # Create order
        sample_order_data["product_id"] = product["id"]
        order_response = await client.post(
            "/api/v1/orders",
            json=sample_order_data,
            params={"user_id": user["id"]}
        )
        order = order_response.json()
        
        # Initiate payment
        payment_data = {
            "order_id": order["id"],
            "type": "PRINT",
            "callback_url": "https://example.com/callback",
        }
        payment_response = await client.post(
            "/api/v1/payments/initiate",
            json=payment_data,
            params={"user_id": user["id"]}
        )
        payment = payment_response.json()
        
        return user, product, order, payment
    
    @pytest.mark.asyncio
    async def test_upload_receipt(self, client: AsyncClient, setup_order_with_payment):
        """Test POST /api/v1/payments/{id}/upload-receipt."""
        user, product, order, payment = await setup_order_with_payment
        
        receipt_data = {
            "receipt_image_url": "https://example.com/receipt.jpg",
        }
        
        response = await client.post(
            f"/api/v1/payments/{payment['payment_id']}/upload-receipt",
            json=receipt_data,
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "AWAITING_APPROVAL"
        assert data["receipt_image_url"] == "https://example.com/receipt.jpg"
    
    @pytest.mark.asyncio
    async def test_get_pending_approval(self, client: AsyncClient, setup_order_with_payment, setup_admin):
        """Test GET /api/v1/payments/pending-approval."""
        user, product, order, payment = await setup_order_with_payment
        admin = await setup_admin
        
        # Upload receipt
        receipt_data = {"receipt_image_url": "https://example.com/receipt.jpg"}
        await client.post(
            f"/api/v1/payments/{payment['payment_id']}/upload-receipt",
            json=receipt_data,
            params={"user_id": user["id"]}
        )
        
        # Get pending approval
        response = await client.get(
            "/api/v1/payments/pending-approval",
            params={"admin_id": admin["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_approve_payment(self, client: AsyncClient, setup_order_with_payment, setup_admin):
        """Test POST /api/v1/payments/{id}/approve."""
        user, product, order, payment = await setup_order_with_payment
        admin = await setup_admin
        
        # Upload receipt
        receipt_data = {"receipt_image_url": "https://example.com/receipt.jpg"}
        await client.post(
            f"/api/v1/payments/{payment['payment_id']}/upload-receipt",
            json=receipt_data,
            params={"user_id": user["id"]}
        )
        
        # Approve
        approve_data = {"admin_id": admin["id"]}
        response = await client.post(
            f"/api/v1/payments/{payment['payment_id']}/approve",
            json=approve_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
    
    @pytest.mark.asyncio
    async def test_reject_payment(self, client: AsyncClient, setup_order_with_payment, setup_admin):
        """Test POST /api/v1/payments/{id}/reject."""
        user, product, order, payment = await setup_order_with_payment
        admin = await setup_admin
        
        # Upload receipt
        receipt_data = {"receipt_image_url": "https://example.com/receipt.jpg"}
        await client.post(
            f"/api/v1/payments/{payment['payment_id']}/upload-receipt",
            json=receipt_data,
            params={"user_id": user["id"]}
        )
        
        # Reject
        reject_data = {"admin_id": admin["id"], "reason": "رسید نامعتبر است"}
        response = await client.post(
            f"/api/v1/payments/{payment['payment_id']}/reject",
            json=reject_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FAILED"
        assert data["rejection_reason"] == "رسید نامعتبر است"

