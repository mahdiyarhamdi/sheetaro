"""Unit tests for SubscriptionService."""

import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import date, timedelta
from decimal import Decimal

from app.services.subscription_service import SubscriptionService
from app.schemas.subscription import SubscriptionCreate
from app.models.enums import SubscriptionPlan
from tests.conftest import create_test_user


class TestSubscriptionService:
    """Test cases for SubscriptionService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create SubscriptionService instance."""
        return SubscriptionService(db_session)
    
    @pytest_asyncio.fixture
    async def test_user(self, db_session):
        """Create a test user."""
        return await create_test_user(db_session)
    
    @pytest.mark.asyncio
    async def test_create_subscription(self, service, test_user):
        """Test creating a subscription."""
        sub_data = SubscriptionCreate(plan=SubscriptionPlan.ADVANCED_SEARCH)
        
        result = await service.create_subscription(test_user.id, sub_data)
        
        assert result is not None
        assert result.user_id == test_user.id
        assert result.plan == SubscriptionPlan.ADVANCED_SEARCH
        assert result.price == Decimal("250000")
        assert result.is_active is True
        assert result.start_date == date.today()
        assert result.end_date == date.today() + timedelta(days=30)
    
    @pytest.mark.asyncio
    async def test_create_subscription_duplicate_fails(self, service, test_user):
        """Test that creating duplicate subscription fails."""
        sub_data = SubscriptionCreate(plan=SubscriptionPlan.ADVANCED_SEARCH)
        
        # Create first subscription
        await service.create_subscription(test_user.id, sub_data)
        
        # Try to create another
        with pytest.raises(ValueError, match="already has an active subscription"):
            await service.create_subscription(test_user.id, sub_data)
    
    @pytest.mark.asyncio
    async def test_get_user_status_with_subscription(self, service, test_user):
        """Test getting user status with active subscription."""
        sub_data = SubscriptionCreate(plan=SubscriptionPlan.ADVANCED_SEARCH)
        await service.create_subscription(test_user.id, sub_data)
        
        result = await service.get_user_status(test_user.id)
        
        assert result.has_active_subscription is True
        assert result.current_subscription is not None
        assert result.days_remaining == 30
    
    @pytest.mark.asyncio
    async def test_get_user_status_without_subscription(self, service, test_user):
        """Test getting user status without subscription."""
        result = await service.get_user_status(test_user.id)
        
        assert result.has_active_subscription is False
        assert result.current_subscription is None
        assert result.days_remaining is None
    
    @pytest.mark.asyncio
    async def test_check_subscription(self, service, test_user):
        """Test checking subscription status."""
        # No subscription
        assert await service.check_subscription(test_user.id) is False
        
        # With subscription
        sub_data = SubscriptionCreate(plan=SubscriptionPlan.ADVANCED_SEARCH)
        await service.create_subscription(test_user.id, sub_data)
        
        assert await service.check_subscription(test_user.id) is True
    
    @pytest.mark.asyncio
    async def test_cancel_subscription(self, service, test_user):
        """Test cancelling subscription."""
        sub_data = SubscriptionCreate(plan=SubscriptionPlan.ADVANCED_SEARCH)
        created = await service.create_subscription(test_user.id, sub_data)
        
        result = await service.cancel_subscription(created.id, test_user.id)
        
        assert result is not None
        assert result.is_active is False
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_wrong_user_fails(self, service, test_user, db_session):
        """Test that wrong user cannot cancel subscription."""
        sub_data = SubscriptionCreate(plan=SubscriptionPlan.ADVANCED_SEARCH)
        created = await service.create_subscription(test_user.id, sub_data)
        
        other_user = await create_test_user(db_session, {
            "telegram_id": 999999999,
            "first_name": "Other",
        })
        
        with pytest.raises(ValueError, match="Access denied"):
            await service.cancel_subscription(created.id, other_user.id)
    
    @pytest.mark.asyncio
    async def test_get_price(self, service):
        """Test getting subscription price."""
        result = service.get_price(SubscriptionPlan.ADVANCED_SEARCH)
        
        assert result["plan"] == "ADVANCED_SEARCH"
        assert result["price"] == Decimal("250000")
        assert result["duration_days"] == 30




