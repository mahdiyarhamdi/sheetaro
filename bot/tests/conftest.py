"""Test configuration and fixtures for bot tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4


@pytest.fixture
def mock_telegram_user():
    """Create a mock Telegram user."""
    user = MagicMock()
    user.id = 123456789
    user.first_name = "Test"
    user.last_name = "User"
    user.username = "testuser"
    user.is_bot = False
    user.language_code = "fa"
    return user


@pytest.fixture
def mock_telegram_chat():
    """Create a mock Telegram chat."""
    chat = MagicMock()
    chat.id = 123456789
    chat.type = "private"
    chat.first_name = "Test"
    return chat


@pytest.fixture
def mock_telegram_message(mock_telegram_user, mock_telegram_chat):
    """Create a mock Telegram message."""
    message = MagicMock()
    message.from_user = mock_telegram_user
    message.chat = mock_telegram_chat
    message.text = ""
    message.reply_text = AsyncMock()
    message.reply_photo = AsyncMock()
    message.delete = AsyncMock()
    return message


@pytest.fixture
def mock_telegram_update(mock_telegram_user, mock_telegram_message):
    """Create a mock Telegram update."""
    update = MagicMock()
    update.update_id = 12345
    update.effective_user = mock_telegram_user
    update.effective_chat = mock_telegram_message.chat
    update.message = mock_telegram_message
    update.callback_query = None
    return update


@pytest.fixture
def mock_callback_query(mock_telegram_user, mock_telegram_chat):
    """Create a mock callback query."""
    callback = MagicMock()
    callback.id = "callback123"
    callback.from_user = mock_telegram_user
    callback.chat_instance = str(mock_telegram_chat.id)
    callback.data = ""
    callback.answer = AsyncMock()
    callback.edit_message_text = AsyncMock()
    callback.edit_message_reply_markup = AsyncMock()
    callback.message = MagicMock()
    callback.message.chat = mock_telegram_chat
    return callback


@pytest.fixture
def mock_telegram_update_with_callback(mock_telegram_user, mock_callback_query):
    """Create a mock Telegram update with callback query."""
    update = MagicMock()
    update.update_id = 12346
    update.effective_user = mock_telegram_user
    update.callback_query = mock_callback_query
    update.message = None
    return update


@pytest.fixture
def mock_context():
    """Create a mock application context."""
    context = MagicMock()
    context.user_data = {}
    context.chat_data = {}
    context.bot_data = {}
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_photo = AsyncMock()
    context.bot.get_file = AsyncMock()
    return context


@pytest.fixture
def sample_user_data():
    """Create sample user data as would be returned from API."""
    return {
        "id": str(uuid4()),
        "telegram_id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "phone_number": "09121234567",
        "role": "CUSTOMER",
        "is_active": True,
    }


@pytest.fixture
def sample_admin_data():
    """Create sample admin user data."""
    return {
        "id": str(uuid4()),
        "telegram_id": 111111111,
        "first_name": "Admin",
        "username": "admin",
        "role": "ADMIN",
        "is_active": True,
    }


@pytest.fixture
def sample_order_data():
    """Create sample order data as would be returned from API."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "product_id": str(uuid4()),
        "design_plan": "PUBLIC",
        "status": "PENDING",
        "quantity": 100,
        "design_price": 0,
        "validation_price": 0,
        "print_price": 100000,
        "total_price": 100000,
        "created_at": "2026-01-04T10:00:00Z",
    }


@pytest.fixture
def sample_payment_data():
    """Create sample payment data."""
    return {
        "payment_id": str(uuid4()),
        "order_id": str(uuid4()),
        "amount": 100000,
        "type": "PRINT",
        "status": "PENDING",
        "created_at": "2026-01-04T10:00:00Z",
    }


@pytest.fixture
def sample_category_data():
    """Create sample category data."""
    return {
        "id": str(uuid4()),
        "name_fa": "برچسب",
        "name_en": "Label",
        "description_fa": "انواع برچسب",
        "is_active": True,
    }


@pytest.fixture
def sample_design_plan_data():
    """Create sample design plan data."""
    return {
        "id": str(uuid4()),
        "category_id": str(uuid4()),
        "plan_type": "PUBLIC",
        "name_fa": "طراحی عمومی",
        "price": 0,
        "has_templates": True,
        "has_questionnaire": False,
    }


@pytest.fixture
def sample_template_data():
    """Create sample template data."""
    return {
        "id": str(uuid4()),
        "plan_id": str(uuid4()),
        "name_fa": "قالب مدرن",
        "image_url": "/files/templates/modern.png",
        "image_width": 800,
        "image_height": 600,
        "placeholder_x": 100,
        "placeholder_y": 100,
        "placeholder_width": 200,
        "placeholder_height": 200,
    }


@pytest.fixture
def mock_api_client():
    """Create a mock API client with common methods."""
    client = MagicMock()
    
    # User methods
    client.get_or_create_user = AsyncMock()
    client.get_user_by_telegram_id = AsyncMock()
    client.promote_to_admin = AsyncMock()
    
    # Order methods
    client.create_order = AsyncMock()
    client.get_user_orders = AsyncMock()
    client.get_order = AsyncMock()
    client.cancel_order = AsyncMock()
    
    # Payment methods
    client.initiate_payment = AsyncMock()
    client.upload_receipt = AsyncMock()
    client.get_pending_payments = AsyncMock()
    client.approve_payment = AsyncMock()
    client.reject_payment = AsyncMock()
    
    # Catalog methods
    client.get_categories = AsyncMock()
    client.get_category = AsyncMock()
    client.create_category = AsyncMock()
    client.get_design_plans = AsyncMock()
    client.get_templates = AsyncMock()
    
    # Settings methods
    client.get_payment_card = AsyncMock()
    
    return client

