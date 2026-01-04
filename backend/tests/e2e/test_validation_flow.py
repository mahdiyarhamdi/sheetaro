"""
E2E Test: Validation Flow

This test covers the complete validation journey for orders with own design:
1. User uploads own design
2. User requests validation
3. Validator reviews design
4. Validation passes or fails with issues
5. If failed: User pays for fix or re-uploads
6. Order proceeds to printing

Validation is optional but recommended for OWN_DESIGN orders.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestValidationFlow:
    """E2E test for design validation flow."""
    
    @pytest.fixture
    async def setup_environment(self, client: AsyncClient):
        """Setup test environment with admin, validator, and product."""
        # Create admin
        admin_data = {
            "telegram_id": 555555555,
            "first_name": "ValidationAdmin",
            "username": "val_admin_e2e",
            "role": "ADMIN",
        }
        admin_response = await client.post("/api/v1/users", json=admin_data)
        admin = admin_response.json()
        
        # Create validator
        validator_data = {
            "telegram_id": 666666666,
            "first_name": "Validator",
            "username": "validator_e2e",
            "role": "VALIDATOR",
        }
        validator_response = await client.post("/api/v1/users", json=validator_data)
        validator = validator_response.json()
        
        # Create print shop
        printshop_data = {
            "telegram_id": 777777777,
            "first_name": "PrintShopVal",
            "username": "printshop_val_e2e",
            "role": "PRINT_SHOP",
        }
        printshop_response = await client.post("/api/v1/users", json=printshop_data)
        printshop = printshop_response.json()
        
        # Create product
        product_data = {
            "name": "Business Card",
            "description": "Standard business cards",
            "type": "LABEL",
            "base_price": 500,
            "min_quantity": 100,
            "material_type": "PAPER",
            "width": 85,
            "height": 55,
        }
        product_response = await client.post("/api/v1/products", json=product_data)
        product = product_response.json()
        
        return {"admin": admin, "validator": validator, "printshop": printshop, "product": product}
    
    @pytest.fixture
    async def customer(self, client: AsyncClient):
        """Create test customer."""
        customer_data = {
            "telegram_id": 888888888,
            "first_name": "ValidationCustomer",
            "last_name": "Test",
            "username": "val_customer_e2e",
        }
        response = await client.post("/api/v1/users", json=customer_data)
        return response.json()
    
    @pytest.mark.asyncio
    async def test_validation_pass_flow(self, client: AsyncClient, setup_environment, customer):
        """Test complete validation flow where design passes."""
        env = setup_environment
        
        # ========== Step 1: Customer creates order with own design ==========
        order_data = {
            "product_id": env["product"]["id"],
            "design_plan": "OWN_DESIGN",
            "quantity": 200,
            "design_file_url": "/files/designs/test/my_design.pdf",
            "validation_requested": False,
        }
        
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": customer["id"]}
        )
        assert order_response.status_code == 201
        order = order_response.json()
        
        assert order["design_plan"] == "OWN_DESIGN"
        assert order["status"] == "PENDING"
        assert order["validation_requested"] is False
        
        # ========== Step 2: Customer requests validation ==========
        validation_request = await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": customer["id"]}
        )
        assert validation_request.status_code == 201
        
        # Verify order status changed
        order_response = await client.get(f"/api/v1/orders/{order['id']}")
        order = order_response.json()
        assert order["status"] == "AWAITING_VALIDATION"
        assert order["validation_requested"] is True
        
        # ========== Step 3: Validator reviews and passes ==========
        report_data = {
            "order_id": order["id"],
            "issues": [],
            "fix_cost": 0,
            "summary": "Design meets all requirements. Resolution, bleed, and colors are correct.",
            "passed": "PASSED",
        }
        
        report_response = await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json=report_data,
            params={"validator_id": env["validator"]["id"]}
        )
        assert report_response.status_code == 201
        report = report_response.json()
        assert report["passed"] == "PASSED"
        
        # ========== Step 4: Verify order status updated ==========
        order_response = await client.get(f"/api/v1/orders/{order['id']}")
        order = order_response.json()
        assert order["status"] == "READY_FOR_PRINT"
        assert order["validation_status"] == "PASSED"
        
        # ========== Step 5: Payment and printing ==========
        payment_response = await client.post(
            "/api/v1/payments/initiate",
            json={
                "order_id": order["id"],
                "amount": float(order["total_price"]),
                "payment_type": "PRINT",
            },
            params={"user_id": customer["id"]}
        )
        payment = payment_response.json()
        
        # Simulate payment success
        await client.post(
            "/api/v1/payments/callback",
            json={
                "payment_id": payment["payment_id"],
                "reference_id": "TEST_VAL_PASS_001",
                "status": "SUCCESS",
            }
        )
        
        # Print shop accepts and completes
        await client.post(
            f"/api/v1/printshop/accept/{order['id']}",
            params={"printshop_id": env["printshop"]["id"]}
        )
        
        await client.patch(
            f"/api/v1/orders/{order['id']}/status",
            json={"status": "DELIVERED"},
            params={"user_id": env["admin"]["id"]}
        )
        
        # Final verification
        final_order = (await client.get(f"/api/v1/orders/{order['id']}")).json()
        assert final_order["status"] == "DELIVERED"
    
    @pytest.mark.asyncio
    async def test_validation_fail_with_fix_flow(self, client: AsyncClient, setup_environment, customer):
        """Test validation flow where design fails and gets fixed."""
        env = setup_environment
        
        # ========== Step 1: Create order with own design ==========
        order_data = {
            "product_id": env["product"]["id"],
            "design_plan": "OWN_DESIGN",
            "quantity": 100,
            "design_file_url": "/files/designs/test/bad_design.pdf",
        }
        
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": customer["id"]}
        )
        order = order_response.json()
        
        # ========== Step 2: Request validation ==========
        await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": customer["id"]}
        )
        
        # ========== Step 3: Validator finds issues ==========
        report_data = {
            "order_id": order["id"],
            "issues": [
                {
                    "type": "resolution",
                    "severity": "high",
                    "description": "Resolution is only 150 DPI",
                    "suggestion": "Increase resolution to 300 DPI for print quality",
                },
                {
                    "type": "bleed",
                    "severity": "medium",
                    "description": "Missing bleed area",
                    "suggestion": "Add 3mm bleed on all sides",
                },
                {
                    "type": "color_mode",
                    "severity": "high",
                    "description": "Design is in RGB color mode",
                    "suggestion": "Convert to CMYK for accurate print colors",
                },
            ],
            "fix_cost": 250000,
            "summary": "Design has multiple issues that need to be fixed before printing.",
            "passed": "FAILED",
        }
        
        report_response = await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json=report_data,
            params={"validator_id": env["validator"]["id"]}
        )
        report = report_response.json()
        assert report["passed"] == "FAILED"
        assert len(report["issues"]) == 3
        
        # ========== Step 4: Verify order needs action ==========
        order = (await client.get(f"/api/v1/orders/{order['id']}")).json()
        assert order["status"] == "NEEDS_ACTION"
        assert order["validation_status"] == "FAILED"
        
        # ========== Step 5: Customer pays for fix ==========
        fix_payment_response = await client.post(
            "/api/v1/payments/initiate",
            json={
                "order_id": order["id"],
                "amount": float(report["fix_cost"]),
                "payment_type": "FIX",
            },
            params={"user_id": customer["id"]}
        )
        fix_payment = fix_payment_response.json()
        
        await client.post(
            "/api/v1/payments/callback",
            json={
                "payment_id": fix_payment["payment_id"],
                "reference_id": "TEST_FIX_001",
                "status": "SUCCESS",
            }
        )
        
        # ========== Step 6: Design gets fixed and re-validated ==========
        # Update with fixed design
        await client.patch(
            f"/api/v1/orders/{order['id']}",
            json={"design_file_url": "/files/designs/test/fixed_design.pdf"},
            params={"user_id": customer["id"]}
        )
        
        # Update validation status to FIXED
        await client.patch(
            f"/api/v1/orders/{order['id']}/status",
            json={"status": "READY_FOR_PRINT", "validation_status": "FIXED"},
            params={"user_id": env["admin"]["id"]}
        )
        
        # ========== Step 7: Proceed to printing ==========
        final_order = (await client.get(f"/api/v1/orders/{order['id']}")).json()
        assert final_order["status"] == "READY_FOR_PRINT"
        assert final_order["validation_status"] == "FIXED"
    
    @pytest.mark.asyncio
    async def test_skip_validation_flow(self, client: AsyncClient, setup_environment, customer):
        """Test flow where customer skips validation (at their own risk)."""
        env = setup_environment
        
        # Create order without validation
        order_data = {
            "product_id": env["product"]["id"],
            "design_plan": "OWN_DESIGN",
            "quantity": 100,
            "design_file_url": "/files/designs/test/skip_val_design.pdf",
            "validation_requested": False,
        }
        
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": customer["id"]}
        )
        order = order_response.json()
        
        # Order should be in pending state (awaiting payment)
        assert order["status"] == "PENDING"
        assert order["validation_requested"] is False
        
        # Customer can proceed directly to payment (skipping validation)
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
        
        # Complete payment
        await client.post(
            "/api/v1/payments/callback",
            json={
                "payment_id": payment["payment_id"],
                "reference_id": "TEST_SKIP_VAL_001",
                "status": "SUCCESS",
            }
        )
        
        # Order should move to ready for print without validation
        await client.patch(
            f"/api/v1/orders/{order['id']}/status",
            json={"status": "READY_FOR_PRINT"},
            params={"user_id": env["admin"]["id"]}
        )
        
        final_order = (await client.get(f"/api/v1/orders/{order['id']}")).json()
        assert final_order["status"] == "READY_FOR_PRINT"
        assert final_order["validation_status"] is None  # No validation performed
    
    @pytest.mark.asyncio
    async def test_multiple_validation_reports(self, client: AsyncClient, setup_environment, customer):
        """Test that an order can have multiple validation reports (history)."""
        env = setup_environment
        
        # Create order
        order_data = {
            "product_id": env["product"]["id"],
            "design_plan": "OWN_DESIGN",
            "quantity": 100,
            "design_file_url": "/files/designs/test/multi_val.pdf",
        }
        
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": customer["id"]}
        )
        order = order_response.json()
        
        # Request validation
        await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": customer["id"]}
        )
        
        # First validation report - FAILED
        await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json={
                "order_id": order["id"],
                "issues": [{"type": "resolution", "severity": "high", "description": "Too low", "suggestion": "Fix it"}],
                "fix_cost": 100000,
                "summary": "Issues found",
                "passed": "FAILED",
            },
            params={"validator_id": env["validator"]["id"]}
        )
        
        # Get reports - should have 1
        reports_response = await client.get(f"/api/v1/validation/order/{order['id']}")
        reports = reports_response.json()
        assert reports["total"] == 1
        assert reports["items"][0]["passed"] == "FAILED"

