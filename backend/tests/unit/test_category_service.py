"""Unit tests for category service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.services.category_service import CategoryService
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut


def make_category_mock(
    category_id=None,
    slug="labels",
    name_fa="لیبل",
    description_fa="انواع لیبل چاپی",
    icon="🏷️",
    sort_order=1,
    is_active=True,
):
    """Create a properly mocked category model."""
    now = datetime.now(timezone.utc)
    mock = MagicMock()
    mock.id = category_id or uuid4()
    mock.slug = slug
    mock.name_fa = name_fa
    mock.description_fa = description_fa
    mock.icon = icon
    mock.sort_order = sort_order
    mock.is_active = is_active
    mock.created_at = now
    mock.updated_at = now
    return mock


class TestCategoryService:
    """Test cases for CategoryService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def sample_category_data(self):
        """Sample category creation data."""
        return CategoryCreate(
            slug="labels",
            name_fa="لیبل",
            description_fa="انواع لیبل چاپی",
            icon="🏷️",
            sort_order=1,
            is_active=True,
        )

    @pytest.fixture
    def sample_category_model(self):
        """Sample category model object with valid datetime fields."""
        return make_category_mock()

    @pytest.mark.asyncio
    async def test_get_all_categories_empty(self, mock_db):
        """Test getting categories when none exist."""
        with patch.object(CategoryRepository, 'get_all_categories', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []
            service = CategoryService(mock_db)
            
            result = await service.get_all_categories()
            
            assert result == []
            mock_get.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_get_all_categories_with_items(self, mock_db, sample_category_model):
        """Test getting categories when some exist."""
        with patch.object(CategoryRepository, 'get_all_categories', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [sample_category_model]
            service = CategoryService(mock_db)
            
            result = await service.get_all_categories()
            
            assert len(result) == 1
            assert result[0].slug == "labels"

    @pytest.mark.asyncio
    async def test_get_category_found(self, mock_db, sample_category_model):
        """Test getting a category that exists."""
        category_id = sample_category_model.id
        with patch.object(CategoryRepository, 'get_category_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_category_model
            service = CategoryService(mock_db)
            
            result = await service.get_category(category_id)
            
            assert result is not None
            assert result.slug == "labels"
            mock_get.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, mock_db):
        """Test getting a category that doesn't exist."""
        category_id = uuid4()
        with patch.object(CategoryRepository, 'get_category_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            service = CategoryService(mock_db)
            
            result = await service.get_category(category_id)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_create_category_success(self, mock_db, sample_category_data, sample_category_model):
        """Test successful category creation."""
        with patch.object(CategoryRepository, 'get_category_by_slug', new_callable=AsyncMock) as mock_slug, \
             patch.object(CategoryRepository, 'create_category', new_callable=AsyncMock) as mock_create:
            mock_slug.return_value = None
            mock_create.return_value = sample_category_model
            service = CategoryService(mock_db)
            
            result = await service.create_category(sample_category_data)
            
            assert result.slug == "labels"
            mock_slug.assert_called_once_with("labels")
            mock_create.assert_called_once_with(sample_category_data)

    @pytest.mark.asyncio
    async def test_create_category_duplicate_slug(self, mock_db, sample_category_data, sample_category_model):
        """Test category creation with duplicate slug."""
        with patch.object(CategoryRepository, 'get_category_by_slug', new_callable=AsyncMock) as mock_slug, \
             patch.object(CategoryRepository, 'create_category', new_callable=AsyncMock) as mock_create:
            mock_slug.return_value = sample_category_model
            service = CategoryService(mock_db)
            
            with pytest.raises(ValueError) as excinfo:
                await service.create_category(sample_category_data)
            
            assert "already exists" in str(excinfo.value)
            mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_category_success(self, mock_db, sample_category_model):
        """Test successful category update."""
        category_id = sample_category_model.id
        update_data = CategoryUpdate(name_fa="لیبل حرفه‌ای")
        updated_model = make_category_mock(category_id=category_id, name_fa="لیبل حرفه‌ای")
        
        with patch.object(CategoryRepository, 'get_category_by_id', new_callable=AsyncMock) as mock_get, \
             patch.object(CategoryRepository, 'update_category', new_callable=AsyncMock) as mock_update:
            mock_get.return_value = sample_category_model
            mock_update.return_value = updated_model
            service = CategoryService(mock_db)
            
            result = await service.update_category(category_id, update_data)
            
            assert result.name_fa == "لیبل حرفه‌ای"

    @pytest.mark.asyncio
    async def test_update_category_not_found(self, mock_db):
        """Test updating a category that doesn't exist."""
        category_id = uuid4()
        update_data = CategoryUpdate(name_fa="لیبل جدید")
        
        with patch.object(CategoryRepository, 'get_category_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            service = CategoryService(mock_db)
            
            with pytest.raises(ValueError) as excinfo:
                await service.update_category(category_id, update_data)
            
            assert "not found" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_update_category_duplicate_slug(self, mock_db, sample_category_model):
        """Test updating category with duplicate slug."""
        category_id = sample_category_model.id
        update_data = CategoryUpdate(slug="invoices")
        other_category = make_category_mock(slug="invoices")
        
        with patch.object(CategoryRepository, 'get_category_by_id', new_callable=AsyncMock) as mock_get, \
             patch.object(CategoryRepository, 'get_category_by_slug', new_callable=AsyncMock) as mock_slug:
            mock_get.return_value = sample_category_model
            mock_slug.return_value = other_category
            service = CategoryService(mock_db)
            
            with pytest.raises(ValueError) as excinfo:
                await service.update_category(category_id, update_data)
            
            assert "already exists" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_delete_category_success(self, mock_db, sample_category_model):
        """Test successful category deletion."""
        category_id = sample_category_model.id
        
        with patch.object(CategoryRepository, 'delete_category', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True
            service = CategoryService(mock_db)
            
            result = await service.delete_category(category_id)
            
            assert result is True
            mock_delete.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, mock_db):
        """Test deleting a category that doesn't exist."""
        category_id = uuid4()
        
        with patch.object(CategoryRepository, 'delete_category', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = False
            service = CategoryService(mock_db)
            
            result = await service.delete_category(category_id)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_get_category_by_slug_found(self, mock_db, sample_category_model):
        """Test getting a category by slug."""
        with patch.object(CategoryRepository, 'get_category_by_slug', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_category_model
            service = CategoryService(mock_db)
            
            result = await service.get_category_by_slug("labels")
            
            assert result is not None
            assert result.slug == "labels"

    @pytest.mark.asyncio
    async def test_get_category_by_slug_not_found(self, mock_db):
        """Test getting a non-existent category by slug."""
        with patch.object(CategoryRepository, 'get_category_by_slug', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            service = CategoryService(mock_db)
            
            result = await service.get_category_by_slug("nonexistent")
            
            assert result is None
