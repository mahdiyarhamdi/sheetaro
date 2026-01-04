"""Integration tests for Validation API."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestValidationAPI:
    """Integration tests for /api/v1/validation endpoints."""
    
    @pytest.fixture
    async def setup_order_with_design(self, client: AsyncClient, sample_user_data, sample_product_data):
        """Create user, product, and order with own design for validation tests."""
        # Create user
        user_response = await client.post("/api/v1/users", json=sample_user_data)
        user = user_response.json()
        
        # Create product
        product_response = await client.post("/api/v1/products", json=sample_product_data)
        product = product_response.json()
        
        # Create order with own design
        order_data = {
            "product_id": product["id"],
            "design_plan": "OWN_DESIGN",
            "quantity": 100,
            "design_file_url": "/files/test/design.pdf",
            "validation_requested": False,
        }
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": user["id"]}
        )
        order = order_response.json()
        
        return user, product, order
    
    @pytest.fixture
    async def setup_validator(self, client: AsyncClient, sample_user_data):
        """Create a validator user."""
        validator_data = sample_user_data.copy()
        validator_data["telegram_id"] = 777666555
        validator_data["first_name"] = "Validator"
        validator_data["role"] = "VALIDATOR"
        
        response = await client.post("/api/v1/users", json=validator_data)
        return response.json()
    
    @pytest.mark.asyncio
    async def test_request_validation(self, client: AsyncClient, setup_order_with_design):
        """Test POST /api/v1/validation/request."""
        user, product, order = setup_order_with_design
        
        response = await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert order["id"] in data["order_id"]
    
    @pytest.mark.asyncio
    async def test_request_validation_updates_order_status(self, client: AsyncClient, setup_order_with_design):
        """Test that validation request updates order status."""
        user, product, order = setup_order_with_design
        
        # Request validation
        await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": user["id"]}
        )
        
        # Check order status
        order_response = await client.get(f"/api/v1/orders/{order['id']}")
        updated_order = order_response.json()
        
        assert updated_order["status"] == "AWAITING_VALIDATION"
        assert updated_order["validation_requested"] is True
    
    @pytest.mark.asyncio
    async def test_submit_validation_report_passed(self, client: AsyncClient, setup_order_with_design, setup_validator):
        """Test POST /api/v1/validation/{order_id}/report - passed."""
        user, product, order = setup_order_with_design
        validator = setup_validator
        
        # First request validation
        await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": user["id"]}
        )
        
        # Submit passing report
        report_data = {
            "order_id": order["id"],
            "issues": [],
            "fix_cost": 0,
            "summary": "Design looks good",
            "passed": "PASSED",
        }
        
        response = await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json=report_data,
            params={"validator_id": validator["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["passed"] == "PASSED"
        
        # Check order moved to READY_FOR_PRINT
        order_response = await client.get(f"/api/v1/orders/{order['id']}")
        updated_order = order_response.json()
        assert updated_order["status"] == "READY_FOR_PRINT"
    
    @pytest.mark.asyncio
    async def test_submit_validation_report_failed(self, client: AsyncClient, setup_order_with_design, setup_validator):
        """Test POST /api/v1/validation/{order_id}/report - failed."""
        user, product, order = setup_order_with_design
        validator = setup_validator
        
        # First request validation
        await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": user["id"]}
        )
        
        # Submit failing report with issues
        report_data = {
            "order_id": order["id"],
            "issues": [
                {
                    "type": "resolution",
                    "severity": "high",
                    "description": "Resolution too low (150 DPI)",
                    "suggestion": "Increase to 300 DPI",
                },
                {
                    "type": "bleed",
                    "severity": "medium",
                    "description": "Missing bleed area",
                    "suggestion": "Add 3mm bleed",
                },
            ],
            "fix_cost": 200000,
            "summary": "Design needs fixes",
            "passed": "FAILED",
        }
        
        response = await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json=report_data,
            params={"validator_id": validator["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["passed"] == "FAILED"
        assert len(data["issues"]) == 2
        assert float(data["fix_cost"]) == 200000
        
        # Check order moved to NEEDS_ACTION
        order_response = await client.get(f"/api/v1/orders/{order['id']}")
        updated_order = order_response.json()
        assert updated_order["status"] == "NEEDS_ACTION"
    
    @pytest.mark.asyncio
    async def test_get_validation_report(self, client: AsyncClient, setup_order_with_design, setup_validator):
        """Test GET /api/v1/validation/{report_id}."""
        user, product, order = setup_order_with_design
        validator = setup_validator
        
        # Request validation and submit report
        await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": user["id"]}
        )
        
        report_data = {
            "order_id": order["id"],
            "issues": [],
            "fix_cost": 0,
            "summary": "Good",
            "passed": "PASSED",
        }
        create_response = await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json=report_data,
            params={"validator_id": validator["id"]}
        )
        report = create_response.json()
        
        # Get report
        response = await client.get(f"/api/v1/validation/{report['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report["id"]
    
    @pytest.mark.asyncio
    async def test_get_order_validation_reports(self, client: AsyncClient, setup_order_with_design, setup_validator):
        """Test GET /api/v1/validation/order/{order_id}."""
        user, product, order = setup_order_with_design
        validator = setup_validator
        
        # Request validation and submit report
        await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": user["id"]}
        )
        
        report_data = {
            "order_id": order["id"],
            "issues": [],
            "fix_cost": 0,
            "summary": "Good",
            "passed": "PASSED",
        }
        await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json=report_data,
            params={"validator_id": validator["id"]}
        )
        
        # Get order reports
        response = await client.get(f"/api/v1/validation/order/{order['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
    
    @pytest.mark.asyncio
    async def test_non_validator_cannot_submit_report(self, client: AsyncClient, setup_order_with_design):
        """Test that non-validator cannot submit validation report."""
        user, product, order = setup_order_with_design
        
        # Request validation
        await client.post(
            "/api/v1/validation/request",
            json={"order_id": order["id"]},
            params={"user_id": user["id"]}
        )
        
        # Try to submit report as customer
        report_data = {
            "order_id": order["id"],
            "issues": [],
            "fix_cost": 0,
            "summary": "Good",
            "passed": "PASSED",
        }
        
        response = await client.post(
            f"/api/v1/validation/{order['id']}/report",
            json=report_data,
            params={"validator_id": user["id"]}  # Customer, not validator
        )
        
        assert response.status_code == 400

