"""Unit tests for ProductService."""

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal

from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.enums import ProductType, MaterialType


class TestProductService:
    """Test cases for ProductService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create ProductService instance."""
        return ProductService(db_session)
    
    @pytest.mark.asyncio
    async def test_create_product(self, service, sample_product_data):
        """Test creating a new product."""
        product_create = ProductCreate(**sample_product_data)
        result = await service.create_product(product_create)
        
        assert result is not None
        assert result.name == sample_product_data["name"]
        assert result.type == ProductType.LABEL
        assert result.base_price == Decimal("10000")
    
    @pytest.mark.asyncio
    async def test_get_product_by_id(self, service, sample_product_data):
        """Test getting product by ID."""
        product_create = ProductCreate(**sample_product_data)
        created = await service.create_product(product_create)
        
        result = await service.get_product_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.name == created.name
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self, service):
        """Test getting non-existent product returns None."""
        result = await service.get_product_by_id(uuid4())
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_products_all(self, service, sample_product_data):
        """Test getting all products."""
        # Create multiple products
        for i in range(3):
            data = sample_product_data.copy()
            data["name"] = f"Product {i}"
            await service.create_product(ProductCreate(**data))
        
        result = await service.get_products()
        
        assert result.total == 3
        assert len(result.items) == 3
    
    @pytest.mark.asyncio
    async def test_get_products_by_type(self, service, sample_product_data):
        """Test filtering products by type."""
        # Create label products
        for i in range(2):
            data = sample_product_data.copy()
            data["name"] = f"Label {i}"
            data["type"] = ProductType.LABEL.value
            await service.create_product(ProductCreate(**data))
        
        # Create invoice product
        invoice_data = sample_product_data.copy()
        invoice_data["name"] = "Invoice"
        invoice_data["type"] = ProductType.INVOICE.value
        invoice_data.pop("material", None)
        await service.create_product(ProductCreate(**invoice_data))
        
        # Filter by LABEL
        result = await service.get_products(product_type=ProductType.LABEL)
        
        assert result.total == 2
        for item in result.items:
            assert item.type == ProductType.LABEL
    
    @pytest.mark.asyncio
    async def test_update_product(self, service, sample_product_data):
        """Test updating product."""
        product_create = ProductCreate(**sample_product_data)
        created = await service.create_product(product_create)
        
        update_data = ProductUpdate(name="Updated Name", base_price=Decimal("20000"))
        result = await service.update_product(created.id, update_data)
        
        assert result is not None
        assert result.name == "Updated Name"
        assert result.base_price == Decimal("20000")
    
    @pytest.mark.asyncio
    async def test_delete_product(self, service, sample_product_data):
        """Test soft deleting product."""
        product_create = ProductCreate(**sample_product_data)
        created = await service.create_product(product_create)
        
        success = await service.delete_product(created.id)
        assert success is True
        
        # Product should not appear in active products
        result = await service.get_products(active_only=True)
        assert all(p.id != created.id for p in result.items)
    
    @pytest.mark.asyncio
    async def test_pagination(self, service, sample_product_data):
        """Test product pagination."""
        # Create 15 products
        for i in range(15):
            data = sample_product_data.copy()
            data["name"] = f"Product {i}"
            await service.create_product(ProductCreate(**data))
        
        # Get first page
        result1 = await service.get_products(page=1, page_size=10)
        assert len(result1.items) == 10
        assert result1.total == 15
        
        # Get second page
        result2 = await service.get_products(page=2, page_size=10)
        assert len(result2.items) == 5





