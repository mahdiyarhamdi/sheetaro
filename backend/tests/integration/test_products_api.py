"""Integration tests for Products API."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestProductsAPI:
    """Integration tests for /api/v1/products endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_product(self, client: AsyncClient, sample_product_data):
        """Test POST /api/v1/products - create new product."""
        response = await client.post("/api/v1/products", json=sample_product_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_product_data["name"]
        assert data["type"] == sample_product_data["type"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_get_products(self, client: AsyncClient, sample_product_data):
        """Test GET /api/v1/products - list products."""
        # Create a product first
        await client.post("/api/v1/products", json=sample_product_data)
        
        response = await client.get("/api/v1/products")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_products_by_type(self, client: AsyncClient, sample_product_data):
        """Test GET /api/v1/products?type=LABEL - filter by type."""
        # Create a label product
        await client.post("/api/v1/products", json=sample_product_data)
        
        response = await client.get("/api/v1/products", params={"type": "LABEL"})
        
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["type"] == "LABEL"
    
    @pytest.mark.asyncio
    async def test_get_product_by_id(self, client: AsyncClient, sample_product_data):
        """Test GET /api/v1/products/{product_id}."""
        # Create product first
        create_response = await client.post("/api/v1/products", json=sample_product_data)
        product_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
    
    @pytest.mark.asyncio
    async def test_get_product_not_found(self, client: AsyncClient):
        """Test GET /api/v1/products/{product_id} - not found."""
        response = await client.get(f"/api/v1/products/{uuid4()}")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_product(self, client: AsyncClient, sample_product_data):
        """Test PATCH /api/v1/products/{product_id}."""
        # Create product first
        create_response = await client.post("/api/v1/products", json=sample_product_data)
        product_id = create_response.json()["id"]
        
        update_data = {"name": "Updated Product", "base_price": 20000}
        response = await client.patch(f"/api/v1/products/{product_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["base_price"] == 20000
    
    @pytest.mark.asyncio
    async def test_delete_product(self, client: AsyncClient, sample_product_data):
        """Test DELETE /api/v1/products/{product_id}."""
        # Create product first
        create_response = await client.post("/api/v1/products", json=sample_product_data)
        product_id = create_response.json()["id"]
        
        response = await client.delete(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 204
        
        # Verify product is not in active list
        list_response = await client.get("/api/v1/products")
        products = list_response.json()["items"]
        assert all(p["id"] != product_id for p in products)
    
    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient, sample_product_data):
        """Test pagination for products list."""
        # Create multiple products
        for i in range(15):
            data = sample_product_data.copy()
            data["name"] = f"Product {i}"
            await client.post("/api/v1/products", json=data)
        
        # Get first page
        response1 = await client.get("/api/v1/products", params={"page": 1, "page_size": 10})
        data1 = response1.json()
        
        assert len(data1["items"]) == 10
        assert data1["page"] == 1
        
        # Get second page
        response2 = await client.get("/api/v1/products", params={"page": 2, "page_size": 10})
        data2 = response2.json()
        
        assert len(data2["items"]) == 5
        assert data2["page"] == 2

