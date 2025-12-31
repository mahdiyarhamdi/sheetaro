"""Product API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.api.deps import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductListResponse
from app.services.product_service import ProductService
from app.models.enums import ProductType

router = APIRouter()


@router.get(
    "/products",
    response_model=ProductListResponse,
    summary="List products",
    description="Get list of products with optional filtering by type and pagination",
)
async def list_products(
    type: Optional[ProductType] = Query(None, description="Filter by product type"),
    active_only: bool = Query(True, description="Show only active products"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """List all products with optional filtering."""
    service = ProductService(db)
    return await service.get_products(
        product_type=type,
        active_only=active_only,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/products/{product_id}",
    response_model=ProductOut,
    summary="Get product by ID",
    description="Retrieve product details by ID",
)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ProductOut:
    """Get product by ID."""
    service = ProductService(db)
    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return product


@router.post(
    "/products",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product (Admin only)",
)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    # TODO: Add admin authentication dependency
) -> ProductOut:
    """Create a new product."""
    service = ProductService(db)
    return await service.create_product(product_data)


@router.patch(
    "/products/{product_id}",
    response_model=ProductOut,
    summary="Update product",
    description="Update product by ID (Admin only)",
)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    # TODO: Add admin authentication dependency
) -> ProductOut:
    """Update product by ID."""
    service = ProductService(db)
    product = await service.update_product(product_id, product_data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return product


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Soft delete product by ID (Admin only)",
)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add admin authentication dependency
) -> None:
    """Delete product by ID."""
    service = ProductService(db)
    success = await service.delete_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )



