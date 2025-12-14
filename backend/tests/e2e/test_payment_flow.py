"""E2E tests for payment flows."""

import pytest
from httpx import AsyncClient


class TestPaymentFlow:
    """End-to-end tests for payment flows."""
    
    @pytest.fixture
    async def setup_order(self, client: AsyncClient, sample_user_data, sample_product_data):
        """Setup user, product, and order for payment tests."""
        # Create user
        user = (await client.post("/api/v1/users", json=sample_user_data)).json()
        
        # Create product
        await client.post("/api/v1/products", json=sample_product_data)
        products = (await client.get("/api/v1/products")).json()["items"]
        product = products[0]
        
        # Create order
        order_data = {
            "product_id": product["id"],
            "design_plan": "PUBLIC",
            "quantity": 100,
        }
        order = (await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": user["id"]}
        )).json()
        
        return user, product, order
    
    @pytest.mark.asyncio
    async def test_payment_success_flow(self, client: AsyncClient, setup_order):
        """Test successful payment flow."""
        user, product, order = setup_order
        
        # Initiate payment
        init_response = await client.post(
            "/api/v1/payments/initiate",
            json={
                "order_id": order["id"],
                "type": "PRINT",
                "callback_url": "https://example.com/callback",
            },
            params={"user_id": user["id"]}
        )
        assert init_response.status_code == 201
        authority = init_response.json()["authority"]
        
        # Simulate successful payment callback
        callback_response = await client.post(
            "/api/v1/payments/callback",
            json={
                "authority": authority,
                "status": "OK",
                "ref_id": "REF123",
            }
        )
        assert callback_response.status_code == 200
        payment = callback_response.json()
        assert payment["status"] == "SUCCESS"
        
        # Verify payment summary
        summary = (await client.get(
            f"/api/v1/payments/order/{order['id']}/summary"
        )).json()
        assert int(float(summary["total_paid"])) == int(float(order["print_price"]))
        assert int(float(summary["total_pending"])) == 0
    
    @pytest.mark.asyncio
    async def test_payment_failed_flow(self, client: AsyncClient, setup_order):
        """Test failed payment flow."""
        user, product, order = setup_order
        
        # Initiate payment
        init_response = await client.post(
            "/api/v1/payments/initiate",
            json={
                "order_id": order["id"],
                "type": "PRINT",
                "callback_url": "https://example.com/callback",
            },
            params={"user_id": user["id"]}
        )
        authority = init_response.json()["authority"]
        
        # Simulate failed payment callback
        callback_response = await client.post(
            "/api/v1/payments/callback",
            json={
                "authority": authority,
                "status": "NOK",
            }
        )
        assert callback_response.status_code == 200
        payment = callback_response.json()
        assert payment["status"] == "FAILED"
        
        # Verify order is still PENDING
        order_check = (await client.get(f"/api/v1/orders/{order['id']}")).json()
        assert order_check["status"] == "PENDING"
    
    @pytest.mark.asyncio
    async def test_subscription_payment_flow(
        self,
        client: AsyncClient,
        sample_user_data,
    ):
        """Test subscription purchase flow."""
        # Create user
        user = (await client.post("/api/v1/users", json=sample_user_data)).json()
        
        # Check initial status
        status1 = (await client.get(
            "/api/v1/subscriptions/me",
            params={"user_id": user["id"]}
        )).json()
        assert status1["has_active_subscription"] is False
        
        # Create subscription
        sub_response = await client.post(
            "/api/v1/subscriptions",
            json={"plan": "ADVANCED_SEARCH"},
            params={"user_id": user["id"]}
        )
        assert sub_response.status_code == 201
        subscription = sub_response.json()
        assert int(float(subscription["price"])) == 250000
        
        # Verify subscription is active
        status2 = (await client.get(
            "/api/v1/subscriptions/me",
            params={"user_id": user["id"]}
        )).json()
        assert status2["has_active_subscription"] is True
        assert status2["days_remaining"] == 30
    
    @pytest.mark.asyncio
    async def test_multiple_payment_types(self, client: AsyncClient, sample_user_data, sample_product_data):
        """Test order with multiple payment types (validation + print)."""
        # Create user
        user = (await client.post("/api/v1/users", json=sample_user_data)).json()
        
        # Create product
        await client.post("/api/v1/products", json=sample_product_data)
        products = (await client.get("/api/v1/products")).json()["items"]
        
        # Create order with validation
        order_data = {
            "product_id": products[0]["id"],
            "design_plan": "OWN_DESIGN",
            "quantity": 100,
            "validation_requested": True,
            "design_file_url": "/files/test/design.pdf",
        }
        order = (await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": user["id"]}
        )).json()
        
        # Verify prices
        assert int(float(order["validation_price"])) == 50000
        assert int(float(order["print_price"])) == int(float(products[0]["base_price"])) * 100
        
        # Pay for validation first
        val_init = (await client.post(
            "/api/v1/payments/initiate",
            json={
                "order_id": order["id"],
                "type": "VALIDATION",
                "callback_url": "https://example.com/callback",
            },
            params={"user_id": user["id"]}
        )).json()
        
        await client.post(
            "/api/v1/payments/callback",
            json={"authority": val_init["authority"], "status": "OK", "ref_id": "VAL1"}
        )
        
        # Pay for print
        print_init = (await client.post(
            "/api/v1/payments/initiate",
            json={
                "order_id": order["id"],
                "type": "PRINT",
                "callback_url": "https://example.com/callback",
            },
            params={"user_id": user["id"]}
        )).json()
        
        await client.post(
            "/api/v1/payments/callback",
            json={"authority": print_init["authority"], "status": "OK", "ref_id": "PRINT1"}
        )
        
        # Verify payment summary shows both
        summary = (await client.get(
            f"/api/v1/payments/order/{order['id']}/summary"
        )).json()
        
        assert len(summary["payments"]) == 2
        assert int(float(summary["total_paid"])) == int(float(order["validation_price"])) + int(float(order["print_price"]))

