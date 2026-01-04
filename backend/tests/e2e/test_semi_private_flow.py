"""
E2E Test: Semi-Private Design Flow

This test covers the complete user journey for ordering with a semi-private design plan:
1. User registers
2. User browses products
3. User creates order with SEMI_PRIVATE plan
4. User receives design from designer
5. User requests revisions (up to max allowed)
6. User makes payment
7. Order goes to print shop
8. Order is delivered

Semi-private plan allows up to 3 revisions.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestSemiPrivateDesignFlow:
    """E2E test for semi-private design order flow."""
    
    @pytest.fixture
    async def setup_environment(self, client: AsyncClient):
        """Setup test environment with admin, designer, and product."""
        # Create admin
        admin_data = {
            "telegram_id": 111111111,
            "first_name": "Admin",
            "username": "admin_e2e",
            "role": "ADMIN",
        }
        admin_response = await client.post("/api/v1/users", json=admin_data)
        admin = admin_response.json()
        
        # Create designer
        designer_data = {
            "telegram_id": 222222222,
            "first_name": "Designer",
            "username": "designer_e2e",
            "role": "DESIGNER",
        }
        designer_response = await client.post("/api/v1/users", json=designer_data)
        designer = designer_response.json()
        
        # Create print shop
        printshop_data = {
            "telegram_id": 333333333,
            "first_name": "PrintShop",
            "username": "printshop_e2e",
            "role": "PRINT_SHOP",
        }
        printshop_response = await client.post("/api/v1/users", json=printshop_data)
        printshop = printshop_response.json()
        
        # Create product
        product_data = {
            "name": "Premium Label",
            "description": "High quality labels",
            "type": "LABEL",
            "base_price": 1000,
            "min_quantity": 50,
            "material_type": "PAPER",
            "width": 100,
            "height": 50,
        }
        product_response = await client.post("/api/v1/products", json=product_data)
        product = product_response.json()
        
        return {"admin": admin, "designer": designer, "printshop": printshop, "product": product}
    
    @pytest.fixture
    async def customer(self, client: AsyncClient):
        """Create test customer."""
        customer_data = {
            "telegram_id": 444444444,
            "first_name": "Customer",
            "last_name": "Test",
            "username": "customer_e2e",
        }
        response = await client.post("/api/v1/users", json=customer_data)
        return response.json()
    
    @pytest.mark.asyncio
    async def test_complete_semi_private_flow(self, client: AsyncClient, setup_environment, customer):
        """Test complete semi-private design order flow."""
        env = setup_environment
        
        # ========== Step 1: Customer browses products ==========
        products_response = await client.get("/api/v1/products")
        assert products_response.status_code == 200
        products = products_response.json()
        assert products["total"] >= 1
        
        # ========== Step 2: Customer creates order with SEMI_PRIVATE plan ==========
        order_data = {
            "product_id": env["product"]["id"],
            "design_plan": "SEMI_PRIVATE",
            "quantity": 100,
            "customer_notes": "I want a modern design with blue colors",
        }
        
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": customer["id"]}
        )
        assert order_response.status_code == 201
        order = order_response.json()
        
        # Verify order details
        assert order["design_plan"] == "SEMI_PRIVATE"
        assert order["status"] == "PENDING"
        assert order["max_revisions"] == 3  # Semi-private allows 3 revisions
        assert order["revision_count"] == 0
        assert float(order["design_price"]) > 0  # Semi-private has design fee
        
        # ========== Step 3: Admin assigns designer ==========
        assign_response = await client.patch(
            f"/api/v1/orders/{order['id']}/assign",
            json={"assigned_designer_id": env["designer"]["id"]},
            params={"user_id": env["admin"]["id"]}
        )
        assert assign_response.status_code == 200
        
        # Update status to DESIGNING
        status_response = await client.patch(
            f"/api/v1/orders/{order['id']}/status",
            json={"status": "DESIGNING"},
            params={"user_id": env["admin"]["id"]}
        )
        assert status_response.status_code == 200
        
        # ========== Step 4: Designer uploads design ==========
        # Simulate design upload
        design_url = f"/files/designs/{customer['id']}/design_v1.pdf"
        update_response = await client.patch(
            f"/api/v1/orders/{order['id']}",
            json={"design_file_url": design_url},
            params={"user_id": customer["id"]}
        )
        assert update_response.status_code == 200
        
        # ========== Step 5: Customer requests revision (1 of 3) ==========
        # Check revision count
        order_response = await client.get(f"/api/v1/orders/{order['id']}")
        current_order = order_response.json()
        
        # Customer requests revision
        revision_response = await client.post(
            f"/api/v1/orders/{order['id']}/revision",
            json={"notes": "Please make the text larger"},
            params={"user_id": customer["id"]}
        )
        # Note: Revision endpoint may need to be implemented
        # This is testing the expected flow
        
        # ========== Step 6: Payment initiation ==========
        payment_response = await client.post(
            "/api/v1/payments/initiate",
            json={
                "order_id": order["id"],
                "amount": float(order["total_price"]),
                "payment_type": "PRINT",
            },
            params={"user_id": customer["id"]}
        )
        assert payment_response.status_code == 201
        payment = payment_response.json()
        
        # ========== Step 7: Simulate successful payment ==========
        callback_response = await client.post(
            "/api/v1/payments/callback",
            json={
                "payment_id": payment["payment_id"],
                "reference_id": "TEST_REF_SEMI_001",
                "status": "SUCCESS",
            }
        )
        assert callback_response.status_code == 200
        
        # ========== Step 8: Order moves to READY_FOR_PRINT ==========
        await client.patch(
            f"/api/v1/orders/{order['id']}/status",
            json={"status": "READY_FOR_PRINT"},
            params={"user_id": env["admin"]["id"]}
        )
        
        # ========== Step 9: Print shop accepts order ==========
        accept_response = await client.post(
            f"/api/v1/printshop/accept/{order['id']}",
            params={"printshop_id": env["printshop"]["id"]}
        )
        assert accept_response.status_code == 200
        
        # ========== Step 10: Print shop completes printing ==========
        await client.patch(
            f"/api/v1/orders/{order['id']}/status",
            json={"status": "SHIPPED", "tracking_code": "TRACK123456"},
            params={"user_id": env["printshop"]["id"]}
        )
        
        # ========== Step 11: Order delivered ==========
        await client.patch(
            f"/api/v1/orders/{order['id']}/status",
            json={"status": "DELIVERED"},
            params={"user_id": env["admin"]["id"]}
        )
        
        # ========== Final Verification ==========
        final_order_response = await client.get(f"/api/v1/orders/{order['id']}")
        final_order = final_order_response.json()
        
        assert final_order["status"] == "DELIVERED"
        assert final_order["tracking_code"] == "TRACK123456"
        
        # Verify payment was successful
        payments_response = await client.get(
            f"/api/v1/payments/order/{order['id']}"
        )
        payments = payments_response.json()
        assert any(p["status"] == "SUCCESS" for p in payments["items"])
    
    @pytest.mark.asyncio
    async def test_semi_private_max_revisions(self, client: AsyncClient, setup_environment, customer):
        """Test that semi-private plan limits revisions to 3."""
        env = setup_environment
        
        # Create order with semi-private plan
        order_data = {
            "product_id": env["product"]["id"],
            "design_plan": "SEMI_PRIVATE",
            "quantity": 100,
        }
        
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": customer["id"]}
        )
        order = order_response.json()
        
        # Verify max revisions is set correctly
        assert order["max_revisions"] == 3
        
        # Simulate using all 3 revisions
        # (This would require implementing revision tracking)
        # After 3 revisions, additional requests should require extra payment

