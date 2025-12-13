"""Unit tests for UserService."""

import pytest
import pytest_asyncio
from uuid import uuid4

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.models.enums import UserRole


class TestUserService:
    """Test cases for UserService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create UserService instance."""
        return UserService(db_session)
    
    @pytest.mark.asyncio
    async def test_create_user(self, service, sample_user_data):
        """Test creating a new user."""
        user_create = UserCreate(**sample_user_data)
        result = await service.create_or_update_user(user_create)
        
        assert result is not None
        assert result.telegram_id == sample_user_data["telegram_id"]
        assert result.first_name == sample_user_data["first_name"]
        assert result.role == UserRole.CUSTOMER
    
    @pytest.mark.asyncio
    async def test_create_user_updates_existing(self, service, sample_user_data):
        """Test that create_or_update updates existing user."""
        user_create = UserCreate(**sample_user_data)
        
        # Create user
        result1 = await service.create_or_update_user(user_create)
        
        # Update user with same telegram_id
        sample_user_data["first_name"] = "Updated"
        user_create2 = UserCreate(**sample_user_data)
        result2 = await service.create_or_update_user(user_create2)
        
        assert result2.id == result1.id
        assert result2.first_name == "Updated"
    
    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id(self, service, sample_user_data):
        """Test getting user by telegram ID."""
        user_create = UserCreate(**sample_user_data)
        created = await service.create_or_update_user(user_create)
        
        result = await service.get_user_by_telegram_id(sample_user_data["telegram_id"])
        
        assert result is not None
        assert result.id == created.id
    
    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_not_found(self, service):
        """Test getting non-existent user returns None."""
        result = await service.get_user_by_telegram_id(999999999)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_user(self, service, sample_user_data):
        """Test updating user."""
        user_create = UserCreate(**sample_user_data)
        await service.create_or_update_user(user_create)
        
        update_data = UserUpdate(first_name="NewName", city="Mashhad")
        result = await service.update_user(sample_user_data["telegram_id"], update_data)
        
        assert result is not None
        assert result.first_name == "NewName"
        assert result.city == "Mashhad"
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, service):
        """Test updating non-existent user returns None."""
        update_data = UserUpdate(first_name="NewName")
        result = await service.update_user(999999999, update_data)
        assert result is None

