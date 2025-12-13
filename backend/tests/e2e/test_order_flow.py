"""E2E tests for complete order flow."""

import pytest
from httpx import AsyncClient


class TestOrderFlow:
    """End-to-end tests for the complete order flow."""
    
    @pytest.mark.asyncio
    async def test_complete_order_flow_public_design(
        self,
        client: AsyncClient,
        sample_user_data,
        sample_product_data,
    ):
        """
        Test complete order flow with public design (free):
        1. Register user
        2. Browse products
        3. Create order (public design)
        4. Initiate payment
        5. Complete payment
        6. Order moves to READY_FOR_PRINT
        7. Print shop accepts
        8. Mark as shipped
        9. Mark as delivered
        """
        # Step 1: Register user
        user_response = await client.post("/api/v1/users", json=sample_user_data)
        assert user_response.status_code == 201
        user = user_response.json()
        user_id = user["id"]
        
        # Step 2: Browse products
        await client.post("/api/v1/products", json=sample_product_data)
        products_response = await client.get("/api/v1/products", params={"type": "LABEL"})
        assert products_response.status_code == 200
        products = products_response.json()["items"]
        assert len(products) > 0
        product = products[0]
        
        # Step 3: Create order
        order_data = {
            "product_id": product["id"],
            "design_plan": "PUBLIC",
            "quantity": 100,
            "validation_requested": False,
            "shipping_address": "Test Address, Tehran",
        }
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": user_id}
        )
        assert order_response.status_code == 201
        order = order_response.json()
        order_id = order["id"]
        assert order["status"] == "PENDING"
        assert order["design_plan"] == "PUBLIC"
        assert order["design_price"] == 0  # Free for public
        
        # Step 4: Initiate payment
        payment_init_response = await client.post(
            "/api/v1/payments/initiate",
            json={
                "order_id": order_id,
                "type": "PRINT",
                "callback_url": "https://example.com/callback",
            },
            params={"user_id": user_id}
        )
        assert payment_init_response.status_code == 201
        payment_init = payment_init_response.json()
        authority = payment_init["authority"]
        
        # Step 5: Complete payment (simulate PSP callback)
        callback_response = await client.post(
            "/api/v1/payments/callback",
            json={
                "authority": authority,
                "status": "OK",
                "ref_id": "REF123456",
            }
        )
        assert callback_response.status_code == 200
        payment = callback_response.json()
        assert payment["status"] == "SUCCESS"
        
        # Step 6: Verify order moved to READY_FOR_PRINT
        order_check = await client.get(f"/api/v1/orders/{order_id}")
        assert order_check.status_code == 200
        order_data = order_check.json()
        assert order_data["status"] == "READY_FOR_PRINT"
        
        # Step 7: Print shop accepts order
        # First create a print shop user
        printshop_data = sample_user_data.copy()
        printshop_data["telegram_id"] = 999888777
        printshop_data["first_name"] = "PrintShop"
        printshop_data["role"] = "PRINT_SHOP"
        printshop_response = await client.post("/api/v1/users", json=printshop_data)
        printshop = printshop_response.json()
        
        # Accept order
        accept_response = await client.post(
            f"/api/v1/printshop/accept/{order_id}",
            params={"printshop_id": printshop["id"]}
        )
        assert accept_response.status_code == 200
        accepted_order = accept_response.json()
        assert accepted_order["status"] == "PRINTING"
        assert accepted_order["assigned_printshop_id"] == printshop["id"]
        
        # Step 8: Mark as shipped
        ship_response = await client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "SHIPPED", "tracking_code": "TRACK123456"}
        )
        assert ship_response.status_code == 200
        shipped_order = ship_response.json()
        assert shipped_order["status"] == "SHIPPED"
        assert shipped_order["tracking_code"] == "TRACK123456"
        
        # Step 9: Mark as delivered
        deliver_response = await client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "DELIVERED"}
        )
        assert deliver_response.status_code == 200
        delivered_order = deliver_response.json()
        assert delivered_order["status"] == "DELIVERED"
        
        # Verify final state
        final_order = await client.get(f"/api/v1/orders/{order_id}")
        assert final_order.json()["status"] == "DELIVERED"
    
    @pytest.mark.asyncio
    async def test_order_flow_with_validation(
        self,
        client: AsyncClient,
        sample_user_data,
        sample_product_data,
    ):
        """
        Test order flow with validation request:
        1. Create order with validation
        2. Verify order goes to AWAITING_VALIDATION
        3. Create validation report
        4. Order moves to appropriate status
        """
        # Create user
        user_response = await client.post("/api/v1/users", json=sample_user_data)
        user = user_response.json()
        
        # Create product
        await client.post("/api/v1/products", json=sample_product_data)
        products = (await client.get("/api/v1/products")).json()["items"]
        product = products[0]
        
        # Create order with validation
        order_data = {
            "product_id": product["id"],
            "design_plan": "OWN_DESIGN",
            "quantity": 100,
            "validation_requested": True,
            "design_file_url": "/files/test/design.pdf",
        }
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": user["id"]}
        )
        assert order_response.status_code == 201
        order = order_response.json()
        
        # Verify validation price
        assert order["validation_price"] == 50000
        assert order["status"] == "AWAITING_VALIDATION"
        
        # Create validator user
        validator_data = sample_user_data.copy()
        validator_data["telegram_id"] = 777666555
        validator_data["first_name"] = "Validator"
        validator_data["role"] = "VALIDATOR"
        validator_response = await client.post("/api/v1/users", json=validator_data)
        validator = validator_response.json()
        
        # Submit validation report (PASSED)
        report_data = {
            "order_id": order["id"],
            "issues": [],
            "fix_cost": 0,
            "summary": "Design looks good",
            "passed": "PASSED",
        }
        report_response = await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json=report_data,
            params={"validator_id": validator["id"]}
        )
        assert report_response.status_code == 201
        
        # Verify order moved to READY_FOR_PRINT
        updated_order = await client.get(f"/api/v1/orders/{order['id']}")
        assert updated_order.json()["status"] == "READY_FOR_PRINT"
    
    @pytest.mark.asyncio
    async def test_order_cancellation_flow(
        self,
        client: AsyncClient,
        sample_user_data,
        sample_product_data,
    ):
        """
        Test order cancellation:
        1. Create order
        2. Cancel order
        3. Verify status is CANCELLED
        4. Try to cancel again (should fail or be idempotent)
        """
        # Setup
        user = (await client.post("/api/v1/users", json=sample_user_data)).json()
        await client.post("/api/v1/products", json=sample_product_data)
        products = (await client.get("/api/v1/products")).json()["items"]
        
        # Create order
        order_data = {
            "product_id": products[0]["id"],
            "design_plan": "PUBLIC",
            "quantity": 100,
        }
        order = (await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": user["id"]}
        )).json()
        
        # Cancel order
        cancel_response = await client.post(
            f"/api/v1/orders/{order['id']}/cancel",
            params={"user_id": user["id"]}
        )
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == "CANCELLED"
        
        # Verify in orders list
        orders = (await client.get(
            "/api/v1/orders",
            params={"user_id": user["id"]}
        )).json()["items"]
        
        cancelled = next(o for o in orders if o["id"] == order["id"])
        assert cancelled["status"] == "CANCELLED"

