"""Unit tests for category service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut


class TestCategoryService:
    """Test cases for CategoryService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create CategoryService with mocked db."""
        return CategoryService(mock_db)

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
        """Sample category model object."""
        mock = MagicMock()
        mock.id = uuid4()
        mock.slug = "labels"
        mock.name_fa = "لیبل"
        mock.description_fa = "انواع لیبل چاپی"
        mock.icon = "🏷️"
        mock.sort_order = 1
        mock.is_active = True
        mock.created_at = None
        mock.updated_at = None
        return mock

    @pytest.mark.asyncio
    async def test_get_all_categories_empty(self, service):
        """Test getting categories when none exist."""
        service.repository.get_all_categories = AsyncMock(return_value=[])
        
        result = await service.get_all_categories()
        
        assert result == []
        service.repository.get_all_categories.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_get_all_categories_with_items(self, service, sample_category_model):
        """Test getting categories when some exist."""
        service.repository.get_all_categories = AsyncMock(
            return_value=[sample_category_model]
        )
        
        result = await service.get_all_categories()
        
        assert len(result) == 1
        assert result[0].slug == "labels"

    @pytest.mark.asyncio
    async def test_get_category_found(self, service, sample_category_model):
        """Test getting a category that exists."""
        category_id = sample_category_model.id
        service.repository.get_category_by_id = AsyncMock(
            return_value=sample_category_model
        )
        
        result = await service.get_category(category_id)
        
        assert result is not None
        assert result.slug == "labels"
        service.repository.get_category_by_id.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, service):
        """Test getting a category that doesn't exist."""
        category_id = uuid4()
        service.repository.get_category_by_id = AsyncMock(return_value=None)
        
        result = await service.get_category(category_id)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_create_category_success(
        self, service, sample_category_data, sample_category_model
    ):
        """Test successful category creation."""
        service.repository.get_category_by_slug = AsyncMock(return_value=None)
        service.repository.create_category = AsyncMock(
            return_value=sample_category_model
        )
        
        result = await service.create_category(sample_category_data)
        
        assert result.slug == "labels"
        service.repository.get_category_by_slug.assert_called_once_with("labels")
        service.repository.create_category.assert_called_once_with(sample_category_data)

    @pytest.mark.asyncio
    async def test_create_category_duplicate_slug(
        self, service, sample_category_data, sample_category_model
    ):
        """Test category creation with duplicate slug."""
        service.repository.get_category_by_slug = AsyncMock(
            return_value=sample_category_model
        )
        
        with pytest.raises(ValueError) as excinfo:
            await service.create_category(sample_category_data)
        
        assert "already exists" in str(excinfo.value)
        service.repository.create_category.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_category_success(self, service, sample_category_model):
        """Test successful category update."""
        category_id = sample_category_model.id
        update_data = CategoryUpdate(name_fa="لیبل حرفه‌ای")
        
        updated_model = MagicMock()
        updated_model.id = category_id
        updated_model.slug = "labels"
        updated_model.name_fa = "لیبل حرفه‌ای"
        updated_model.description_fa = "انواع لیبل چاپی"
        updated_model.icon = "🏷️"
        updated_model.sort_order = 1
        updated_model.is_active = True
        updated_model.created_at = None
        updated_model.updated_at = None
        
        service.repository.get_category_by_id = AsyncMock(
            return_value=sample_category_model
        )
        service.repository.update_category = AsyncMock(return_value=updated_model)
        
        result = await service.update_category(category_id, update_data)
        
        assert result.name_fa == "لیبل حرفه‌ای"

    @pytest.mark.asyncio
    async def test_update_category_not_found(self, service):
        """Test updating a category that doesn't exist."""
        category_id = uuid4()
        update_data = CategoryUpdate(name_fa="لیبل جدید")
        
        service.repository.get_category_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError) as excinfo:
            await service.update_category(category_id, update_data)
        
        assert "not found" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_update_category_duplicate_slug(self, service, sample_category_model):
        """Test updating category with duplicate slug."""
        category_id = sample_category_model.id
        update_data = CategoryUpdate(slug="invoices")
        
        other_category = MagicMock()
        other_category.id = uuid4()
        other_category.slug = "invoices"
        
        service.repository.get_category_by_id = AsyncMock(
            return_value=sample_category_model
        )
        service.repository.get_category_by_slug = AsyncMock(return_value=other_category)
        
        with pytest.raises(ValueError) as excinfo:
            await service.update_category(category_id, update_data)
        
        assert "already exists" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_delete_category_success(self, service, sample_category_model):
        """Test successful category deletion."""
        category_id = sample_category_model.id
        
        service.repository.get_category_by_id = AsyncMock(
            return_value=sample_category_model
        )
        service.repository.delete_category = AsyncMock(return_value=True)
        
        result = await service.delete_category(category_id)
        
        assert result is True
        service.repository.delete_category.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, service):
        """Test deleting a category that doesn't exist."""
        category_id = uuid4()
        
        service.repository.get_category_by_id = AsyncMock(return_value=None)
        
        result = await service.delete_category(category_id)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_category_by_slug_found(self, service, sample_category_model):
        """Test getting a category by slug."""
        service.repository.get_category_by_slug = AsyncMock(
            return_value=sample_category_model
        )
        
        result = await service.get_category_by_slug("labels")
        
        assert result is not None
        assert result.slug == "labels"

    @pytest.mark.asyncio
    async def test_get_category_by_slug_not_found(self, service):
        """Test getting a non-existent category by slug."""
        service.repository.get_category_by_slug = AsyncMock(return_value=None)
        
        result = await service.get_category_by_slug("nonexistent")
        
        assert result is None

