"""Unit tests for SettingsService."""

import pytest
import pytest_asyncio
from uuid import uuid4

from app.services.settings_service import SettingsService
from app.schemas.settings import PaymentCardInfo
from app.models.enums import UserRole
from tests.conftest import create_test_user


class TestSettingsService:
    """Test cases for SettingsService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create SettingsService instance."""
        return SettingsService(db_session)
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user."""
        return await create_test_user(db_session, {
            "telegram_id": 111111111,
            "first_name": "Admin",
            "role": UserRole.ADMIN,
        })
    
    @pytest.mark.asyncio
    async def test_get_payment_card_not_set(self, service):
        """Test getting payment card when not set."""
        result = await service.get_payment_card()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_payment_card(self, service, admin_user):
        """Test setting payment card info."""
        card_info = PaymentCardInfo(
            card_number="6219861973679219",
            card_holder="Test User",
        )
        
        result = await service.set_payment_card(card_info, admin_user.id)
        
        assert result is not None
        assert result.card_number == "6219861973679219"
        assert result.card_holder == "Test User"
    
    @pytest.mark.asyncio
    async def test_get_payment_card_after_set(self, service, admin_user):
        """Test getting payment card after setting."""
        card_info = PaymentCardInfo(
            card_number="6219861973679219",
            card_holder="Test User",
        )
        await service.set_payment_card(card_info, admin_user.id)
        
        result = await service.get_payment_card()
        
        assert result is not None
        assert result.card_number == "6219861973679219"
        assert result.card_holder == "Test User"
    
    @pytest.mark.asyncio
    async def test_update_payment_card(self, service, admin_user):
        """Test updating payment card info."""
        # Set initial
        card_info = PaymentCardInfo(
            card_number="6219861973679219",
            card_holder="Test User",
        )
        await service.set_payment_card(card_info, admin_user.id)
        
        # Update
        from app.schemas.settings import PaymentCardUpdate
        update_data = PaymentCardUpdate(card_holder="New Name")
        result = await service.update_payment_card(update_data, admin_user.id)
        
        assert result is not None
        assert result.card_number == "6219861973679219"  # Unchanged
        assert result.card_holder == "New Name"  # Updated
    
    @pytest.mark.asyncio
    async def test_get_setting(self, service, admin_user):
        """Test getting a generic setting."""
        # Set a setting
        await service.set_setting("test_key", "test_value", admin_user.id)
        
        result = await service.get_setting("test_key")
        
        assert result is not None
        assert result.value == "test_value"
    
    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, service):
        """Test getting non-existent setting."""
        result = await service.get_setting("non_existent_key")
        assert result is None

