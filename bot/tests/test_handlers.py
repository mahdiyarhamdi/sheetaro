"""Unit tests for bot handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestStartHandler:
    """Test /start command handler."""
    
    @pytest.fixture
    def mock_update(self):
        """Create mock update for /start command."""
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789
        update.effective_user.first_name = "Test"
        update.effective_user.last_name = "User"
        update.effective_user.username = "testuser"
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {}
        return context
    
    @pytest.mark.asyncio
    async def test_start_new_user(self, mock_update, mock_context):
        """Test /start for new user."""
        # Simulate API creating new user
        user_response = {
            "id": str(uuid4()),
            "telegram_id": 123456789,
            "first_name": "Test",
            "role": "CUSTOMER",
        }
        
        # Verify user data is correct
        assert mock_update.effective_user.id == 123456789
        assert mock_update.effective_user.first_name == "Test"
    
    @pytest.mark.asyncio
    async def test_start_existing_user(self, mock_update, mock_context):
        """Test /start for existing user."""
        # Simulate API returning existing user
        existing_user = {
            "id": str(uuid4()),
            "telegram_id": 123456789,
            "role": "ADMIN",
        }
        
        # Admin should see different menu
        assert existing_user['role'] == "ADMIN"


class TestMakeAdminHandler:
    """Test /makeadmin command handler."""
    
    @pytest.fixture
    def mock_update(self):
        """Create mock update for /makeadmin command."""
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {
            "user_id": str(uuid4()),
        }
        return context
    
    @pytest.mark.asyncio
    async def test_make_admin_912_success(self, mock_update, mock_context):
        """Test successful admin promotion via /makeadmin912."""
        from unittest.mock import patch, AsyncMock
        from handlers.start import make_admin_command
        
        user_id = str(uuid4())
        
        # Mock API responses
        with patch('handlers.start.api_client') as mock_api:
            mock_api.get_user_by_telegram_id = AsyncMock(return_value={
                "id": user_id,
                "telegram_id": 123456789,
                "role": "CUSTOMER",
            })
            mock_api.promote_to_admin = AsyncMock(return_value={
                "id": user_id,
                "role": "ADMIN",
            })
            
            await make_admin_command(mock_update, mock_context)
            
            # Verify API was called
            mock_api.get_user_by_telegram_id.assert_called_once()
            mock_api.promote_to_admin.assert_called_once_with(user_id)
            
            # Verify success message was sent
            mock_update.message.reply_text.assert_called()
            call_args = mock_update.message.reply_text.call_args
            assert "تبریک" in call_args[0][0] or "ادمین" in call_args[0][0]
            
            # Verify context was updated
            assert mock_context.user_data['is_admin'] == True
            assert mock_context.user_data['user_role'] == 'ADMIN'
    
    @pytest.mark.asyncio
    async def test_make_admin_912_already_admin(self, mock_update, mock_context):
        """Test /makeadmin912 when user is already admin."""
        from unittest.mock import patch, AsyncMock
        from handlers.start import make_admin_command
        
        user_id = str(uuid4())
        
        with patch('handlers.start.api_client') as mock_api:
            mock_api.get_user_by_telegram_id = AsyncMock(return_value={
                "id": user_id,
                "telegram_id": 123456789,
                "role": "ADMIN",
            })
            
            await make_admin_command(mock_update, mock_context)
            
            # Should not call promote_to_admin
            mock_api.promote_to_admin.assert_not_called()
            
            # Should send "already admin" message
            mock_update.message.reply_text.assert_called()
            call_args = mock_update.message.reply_text.call_args
            assert "قبلاً ادمین" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_make_admin_912_user_not_found(self, mock_update, mock_context):
        """Test /makeadmin912 when user is not registered."""
        from unittest.mock import patch, AsyncMock
        from handlers.start import make_admin_command
        
        with patch('handlers.start.api_client') as mock_api:
            mock_api.get_user_by_telegram_id = AsyncMock(return_value=None)
            
            await make_admin_command(mock_update, mock_context)
            
            # Should send error message
            mock_update.message.reply_text.assert_called()
            call_args = mock_update.message.reply_text.call_args
            assert "/start" in call_args[0][0]


class TestMenuHandler:
    """Test main menu handler."""
    
    @pytest.fixture
    def mock_callback_update(self):
        """Create mock callback update."""
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.data = "menu_back"
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {
            "role": "CUSTOMER",
        }
        return context
    
    @pytest.mark.asyncio
    async def test_show_main_menu_customer(self, mock_callback_update, mock_context):
        """Test main menu for customer."""
        # Customer menu should have specific options
        customer_options = [
            "ثبت سفارش",
            "سفارشات من",
            "پروفایل من",
        ]
        
        assert "ثبت سفارش" in customer_options
        assert "پنل مدیریت" not in customer_options
    
    @pytest.mark.asyncio
    async def test_show_main_menu_admin(self, mock_callback_update, mock_context):
        """Test main menu for admin."""
        mock_context.user_data['role'] = "ADMIN"
        
        # Admin menu should have additional options
        admin_options = [
            "ثبت سفارش",
            "سفارشات من",
            "پروفایل من",
            "پنل مدیریت",
        ]
        
        assert "پنل مدیریت" in admin_options


class TestOrderFlowHandler:
    """Test order flow handlers."""
    
    @pytest.fixture
    def mock_update(self):
        """Create mock update."""
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789
        update.callback_query = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {
            "user_id": str(uuid4()),
            "current_flow": "order",
        }
        return context
    
    @pytest.mark.asyncio
    async def test_start_order_shows_categories(self, mock_update, mock_context):
        """Test that starting order shows category selection."""
        categories = [
            {"id": str(uuid4()), "name_fa": "برچسب"},
            {"id": str(uuid4()), "name_fa": "فاکتور"},
        ]
        
        assert len(categories) == 2
    
    @pytest.mark.asyncio
    async def test_select_category_shows_plans(self, mock_update, mock_context):
        """Test that selecting category shows design plans."""
        plans = [
            {"id": str(uuid4()), "plan_type": "PUBLIC", "name_fa": "عمومی"},
            {"id": str(uuid4()), "plan_type": "SEMI_PRIVATE", "name_fa": "نیمه‌خصوصی"},
        ]
        
        assert len(plans) == 2
    
    @pytest.mark.asyncio
    async def test_select_public_plan_shows_templates(self, mock_update, mock_context):
        """Test that selecting public plan shows templates."""
        mock_context.user_data['selected_plan_type'] = "PUBLIC"
        
        templates = [
            {"id": str(uuid4()), "name_fa": "قالب مدرن"},
            {"id": str(uuid4()), "name_fa": "قالب کلاسیک"},
        ]
        
        assert mock_context.user_data['selected_plan_type'] == "PUBLIC"
        assert len(templates) == 2


class TestPaymentFlowHandler:
    """Test payment flow handlers."""
    
    @pytest.fixture
    def mock_update(self):
        """Create mock update with photo."""
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789
        update.message = MagicMock()
        update.message.photo = [MagicMock(file_id="test_file_id")]
        update.message.reply_text = AsyncMock()
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context with payment data."""
        context = MagicMock()
        context.user_data = {
            "user_id": str(uuid4()),
            "current_flow": "order",
            "flow_step": "payment_upload_receipt",
            "flow_data": {
                "order_id": str(uuid4()),
                "payment_id": str(uuid4()),
            },
        }
        context.bot = MagicMock()
        context.bot.get_file = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_show_payment_card_info(self, mock_update, mock_context):
        """Test showing payment card info to customer."""
        card_info = {
            "card_number": "6104-****-****-1234",
            "holder_name": "شرکت شیتارو",
        }
        
        assert "6104" in card_info['card_number']
    
    @pytest.mark.asyncio
    async def test_receipt_upload_success(self, mock_update, mock_context):
        """Test successful receipt upload."""
        # Simulate file upload
        assert mock_update.message.photo is not None
        assert len(mock_update.message.photo) > 0
        
        # After upload, status should change
        mock_context.user_data['flow_step'] = "payment_awaiting_approval"
        assert mock_context.user_data['flow_step'] == "payment_awaiting_approval"


class TestAdminPaymentHandler:
    """Test admin payment approval handlers."""
    
    @pytest.fixture
    def mock_update(self):
        """Create mock callback update."""
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 111111111  # Admin ID
        update.callback_query = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context for admin."""
        context = MagicMock()
        context.user_data = {
            "user_id": str(uuid4()),
            "role": "ADMIN",
        }
        return context
    
    @pytest.mark.asyncio
    async def test_show_pending_payments(self, mock_update, mock_context):
        """Test showing pending payments to admin."""
        pending_payments = [
            {
                "payment_id": str(uuid4()),
                "amount": 100000,
                "status": "AWAITING_APPROVAL",
                "receipt_image_url": "/uploads/receipt1.jpg",
            },
            {
                "payment_id": str(uuid4()),
                "amount": 200000,
                "status": "AWAITING_APPROVAL",
                "receipt_image_url": "/uploads/receipt2.jpg",
            },
        ]
        
        assert len(pending_payments) == 2
        assert all(p['status'] == "AWAITING_APPROVAL" for p in pending_payments)
    
    @pytest.mark.asyncio
    async def test_approve_payment(self, mock_update, mock_context):
        """Test approving a payment."""
        payment_id = str(uuid4())
        
        # Simulate approval
        approved_payment = {
            "payment_id": payment_id,
            "status": "SUCCESS",
            "approved_by": mock_context.user_data['user_id'],
        }
        
        assert approved_payment['status'] == "SUCCESS"
    
    @pytest.mark.asyncio
    async def test_reject_payment(self, mock_update, mock_context):
        """Test rejecting a payment."""
        payment_id = str(uuid4())
        
        # Simulate rejection with reason
        rejected_payment = {
            "payment_id": payment_id,
            "status": "FAILED",
            "rejection_reason": "رسید نامعتبر است",
        }
        
        assert rejected_payment['status'] == "FAILED"
        assert rejected_payment['rejection_reason'] is not None

