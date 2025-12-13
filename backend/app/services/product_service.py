"""Product service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductListResponse
from app.models.enums import ProductType
from app.utils.logger import log_event


class ProductService:
    """Service layer for product business logic."""
    
    def __init__(self, db: AsyncSession):
        self.repository = ProductRepository(db)
    
    async def create_product(self, product_data: ProductCreate) -> ProductOut:
        """Create a new product."""
        product = await self.repository.create(product_data)
        
        log_event(
            event_type="product.create",
            product_id=str(product.id),
            product_type=product.type.value,
            name=product.name,
        )
        
        return ProductOut.model_validate(product)
    
    async def get_product_by_id(self, product_id: UUID) -> Optional[ProductOut]:
        """Get product by ID."""
        product = await self.repository.get_by_id(product_id)
        if product:
            return ProductOut.model_validate(product)
        return None
    
    async def get_products(
        self,
        product_type: Optional[ProductType] = None,
        active_only: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> ProductListResponse:
        """Get list of products with filtering and pagination."""
        # Validate page_size
        page_size = min(page_size, 100)  # Max 100 items per page
        page = max(page, 1)
        
        products, total = await self.repository.get_all(
            product_type=product_type,
            active_only=active_only,
            page=page,
            page_size=page_size,
        )
        
        return ProductListResponse(
            items=[ProductOut.model_validate(p) for p in products],
            total=total,
            page=page,
            page_size=page_size,
        )
    
    async def update_product(self, product_id: UUID, product_data: ProductUpdate) -> Optional[ProductOut]:
        """Update product by ID."""
        product = await self.repository.update(product_id, product_data)
        if product:
            log_event(
                event_type="product.update",
                product_id=str(product.id),
            )
            return ProductOut.model_validate(product)
        return None
    
    async def delete_product(self, product_id: UUID) -> bool:
        """Soft delete product by ID."""
        success = await self.repository.delete(product_id)
        if success:
            log_event(
                event_type="product.delete",
                product_id=str(product_id),
            )
        return success

