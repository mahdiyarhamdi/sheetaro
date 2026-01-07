"""Product repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import Optional
from uuid import UUID

from app.models.product import Product
from app.models.enums import ProductType
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    """Repository for product database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        product = Product(**product_data.model_dump())
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get product by ID."""
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        product_type: Optional[ProductType] = None,
        active_only: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Product], int]:
        """Get all products with optional filtering and pagination."""
        query = select(Product)
        count_query = select(func.count(Product.id))
        
        if product_type:
            query = query.where(Product.type == product_type)
            count_query = count_query.where(Product.type == product_type)
        
        if active_only:
            query = query.where(Product.is_active == True)
            count_query = count_query.where(Product.is_active == True)
        
        # Order by sort_order, then by name
        query = query.order_by(Product.sort_order, Product.name)
        
        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute queries
        result = await self.db.execute(query)
        products = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return products, total
    
    async def update(self, product_id: UUID, product_data: ProductUpdate) -> Optional[Product]:
        """Update product by ID."""
        update_data = product_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(product_id)
        
        await self.db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(product_id)
    
    async def delete(self, product_id: UUID) -> bool:
        """Soft delete product by setting is_active to False."""
        product = await self.get_by_id(product_id)
        if not product:
            return False
        
        await self.db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(is_active=False)
        )
        await self.db.flush()
        return True





