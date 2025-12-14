"""Unit tests for UserService."""

import pytest
import pytest_asyncio
from uuid import uuid4

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.models.enums import UserRole
from tests.conftest import create_test_user


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


class TestAdminManagement:
    """Test cases for admin management in UserService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create UserService instance."""
        return UserService(db_session)
    
    @pytest_asyncio.fixture
    async def admin_user(self, service, db_session):
        """Create an admin user."""
        from tests.conftest import create_test_user
        return await create_test_user(db_session, {
            "telegram_id": 111111111,
            "first_name": "Admin",
            "role": UserRole.ADMIN,
        })
    
    @pytest_asyncio.fixture
    async def regular_user(self, service, db_session):
        """Create a regular user."""
        from tests.conftest import create_test_user
        return await create_test_user(db_session, {
            "telegram_id": 222222222,
            "first_name": "Regular",
            "role": UserRole.CUSTOMER,
        })
    
    @pytest.mark.asyncio
    async def test_get_all_admins(self, service, admin_user):
        """Test getting all admin users."""
        result = await service.get_all_admins()
        
        assert len(result) >= 1
        assert any(a.telegram_id == admin_user.telegram_id for a in result)
    
    @pytest.mark.asyncio
    async def test_get_admin_telegram_ids(self, service, admin_user):
        """Test getting admin telegram IDs."""
        result = await service.get_admin_telegram_ids()
        
        assert admin_user.telegram_id in result
    
    @pytest.mark.asyncio
    async def test_promote_to_admin(self, service, admin_user, regular_user):
        """Test promoting a user to admin."""
        result = await service.promote_to_admin(
            target_telegram_id=regular_user.telegram_id,
            admin_id=admin_user.id,
        )
        
        assert result is not None
        assert result.role == UserRole.ADMIN
    
    @pytest.mark.asyncio
    async def test_promote_to_admin_non_admin_fails(self, service, regular_user, db_session):
        """Test that non-admin cannot promote users."""
        from tests.conftest import create_test_user
        other_user = await create_test_user(db_session, {
            "telegram_id": 333333333,
            "first_name": "Other",
            "role": UserRole.CUSTOMER,
        })
        
        with pytest.raises(ValueError, match="Admin access required"):
            await service.promote_to_admin(
                target_telegram_id=other_user.telegram_id,
                admin_id=regular_user.id,
            )
    
    @pytest.mark.asyncio
    async def test_promote_already_admin_fails(self, service, admin_user, db_session):
        """Test that promoting existing admin fails."""
        from tests.conftest import create_test_user
        other_admin = await create_test_user(db_session, {
            "telegram_id": 444444444,
            "first_name": "OtherAdmin",
            "role": UserRole.ADMIN,
        })
        
        with pytest.raises(ValueError, match="already an admin"):
            await service.promote_to_admin(
                target_telegram_id=other_admin.telegram_id,
                admin_id=admin_user.id,
            )
    
    @pytest.mark.asyncio
    async def test_demote_from_admin(self, service, admin_user, db_session):
        """Test demoting an admin to customer."""
        from tests.conftest import create_test_user
        other_admin = await create_test_user(db_session, {
            "telegram_id": 555555555,
            "first_name": "ToRemove",
            "role": UserRole.ADMIN,
        })
        
        result = await service.demote_from_admin(
            target_telegram_id=other_admin.telegram_id,
            admin_id=admin_user.id,
        )
        
        assert result is not None
        assert result.role == UserRole.CUSTOMER
    
    @pytest.mark.asyncio
    async def test_demote_last_admin_fails(self, service, db_session):
        """Test that last admin cannot be demoted."""
        from tests.conftest import create_test_user
        only_admin = await create_test_user(db_session, {
            "telegram_id": 666666666,
            "first_name": "OnlyAdmin",
            "role": UserRole.ADMIN,
        })
        
        with pytest.raises(ValueError, match="last admin"):
            await service.demote_from_admin(
                target_telegram_id=only_admin.telegram_id,
                admin_id=only_admin.id,
            )

