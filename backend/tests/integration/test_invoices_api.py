"""Integration tests for Invoices API."""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import date
from decimal import Decimal


class TestInvoicesAPI:
    """Integration tests for /api/v1/invoices endpoints."""
    
    @pytest.fixture
    async def setup_delivered_order(self, client: AsyncClient, sample_user_data, sample_product_data):
        """Create user, product, and delivered order for invoice tests."""
        # Create user
        user_response = await client.post("/api/v1/users", json=sample_user_data)
        user = user_response.json()
        
        # Create product
        product_response = await client.post("/api/v1/products", json=sample_product_data)
        product = product_response.json()
        
        # Create order
        order_data = {
            "product_id": product["id"],
            "design_plan": "PUBLIC",
            "quantity": 100,
        }
        order_response = await client.post(
            "/api/v1/orders",
            json=order_data,
            params={"user_id": user["id"]}
        )
        order = order_response.json()
        
        # Update order to DELIVERED status
        await client.patch(
            f"/api/v1/orders/{order['id']}/status",
            json={"status": "DELIVERED"},
            params={"user_id": user["id"]}
        )
        
        return user, product, order
    
    @pytest.mark.asyncio
    async def test_create_invoice(self, client: AsyncClient, setup_delivered_order):
        """Test POST /api/v1/invoices - create new invoice."""
        user, product, order = setup_delivered_order
        
        invoice_data = {
            "order_id": order["id"],
            "customer_name": "Test Company",
            "customer_code": "TC001",
            "customer_address": "Tehran, Iran",
            "customer_phone": "09121234567",
            "items": [
                {
                    "description": "Label print",
                    "quantity": 100,
                    "unit_price": 1000,
                    "total": 100000,
                }
            ],
            "tax_amount": 9000,
            "discount_amount": 0,
            "issue_date": date.today().isoformat(),
        }
        
        response = await client.post(
            "/api/v1/invoices",
            json=invoice_data,
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "Test Company"
        assert "invoice_number" in data
        assert len(data["items"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_invoice_by_number(self, client: AsyncClient, setup_delivered_order):
        """Test GET /api/v1/invoices/{invoice_number}."""
        user, product, order = setup_delivered_order
        
        # Create invoice
        invoice_data = {
            "order_id": order["id"],
            "customer_name": "Test",
            "items": [{"description": "Item", "quantity": 1, "unit_price": 1000, "total": 1000}],
            "issue_date": date.today().isoformat(),
        }
        create_response = await client.post(
            "/api/v1/invoices",
            json=invoice_data,
            params={"user_id": user["id"]}
        )
        invoice = create_response.json()
        
        # Get by number
        response = await client.get(f"/api/v1/invoices/{invoice['invoice_number']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["invoice_number"] == invoice["invoice_number"]
    
    @pytest.mark.asyncio
    async def test_list_user_invoices(self, client: AsyncClient, setup_delivered_order):
        """Test GET /api/v1/invoices - list user invoices."""
        user, product, order = setup_delivered_order
        
        # Create multiple invoices
        for i in range(3):
            invoice_data = {
                "order_id": order["id"],
                "customer_name": f"Customer {i}",
                "items": [{"description": f"Item {i}", "quantity": 1, "unit_price": 1000, "total": 1000}],
                "issue_date": date.today().isoformat(),
            }
            await client.post(
                "/api/v1/invoices",
                json=invoice_data,
                params={"user_id": user["id"]}
            )
        
        response = await client.get(
            "/api/v1/invoices",
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
    
    @pytest.mark.asyncio
    async def test_update_invoice(self, client: AsyncClient, setup_delivered_order):
        """Test PATCH /api/v1/invoices/{id}."""
        user, product, order = setup_delivered_order
        
        # Create invoice
        invoice_data = {
            "order_id": order["id"],
            "customer_name": "Original Name",
            "items": [{"description": "Item", "quantity": 1, "unit_price": 1000, "total": 1000}],
            "issue_date": date.today().isoformat(),
        }
        create_response = await client.post(
            "/api/v1/invoices",
            json=invoice_data,
            params={"user_id": user["id"]}
        )
        invoice = create_response.json()
        
        # Update
        update_response = await client.patch(
            f"/api/v1/invoices/{invoice['id']}",
            json={"customer_name": "Updated Name"},
            params={"user_id": user["id"]}
        )
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["customer_name"] == "Updated Name"
    
    @pytest.mark.asyncio
    async def test_generate_pdf(self, client: AsyncClient, setup_delivered_order):
        """Test POST /api/v1/invoices/{id}/pdf."""
        user, product, order = setup_delivered_order
        
        # Create invoice
        invoice_data = {
            "order_id": order["id"],
            "customer_name": "Test",
            "items": [{"description": "Item", "quantity": 1, "unit_price": 1000, "total": 1000}],
            "issue_date": date.today().isoformat(),
        }
        create_response = await client.post(
            "/api/v1/invoices",
            json=invoice_data,
            params={"user_id": user["id"]}
        )
        invoice = create_response.json()
        
        # Generate PDF
        response = await client.post(
            f"/api/v1/invoices/{invoice['id']}/pdf",
            params={"user_id": user["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "pdf_url" in data
        assert data["pdf_url"].endswith(".pdf")
    
    @pytest.mark.asyncio
    async def test_search_invoices_requires_subscription(self, client: AsyncClient, setup_delivered_order):
        """Test GET /api/v1/invoices/search requires subscription."""
        user, product, order = setup_delivered_order
        
        response = await client.get(
            "/api/v1/invoices/search",
            params={
                "user_id": user["id"],
                "customer_name": "Test",
                "has_subscription": "false",
            }
        )
        
        # Should fail without subscription
        assert response.status_code == 400

