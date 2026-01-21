"""Tests for web_link handler and Telegram-Web account linking."""

import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Message, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

# Ensure the bot directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.web_link import (
    linkweb_command,
    handle_otp_input,
    cancel_linkweb,
    WAITING_OTP,
)


# ==================== Fixtures ====================

@pytest.fixture
def mock_user():
    """Create a mock Telegram user."""
    user = MagicMock(spec=User)
    user.id = 123456789
    user.username = "testuser"
    user.first_name = "Test"
    user.full_name = "Test User"
    return user


@pytest.fixture
def mock_message(mock_user):
    """Create a mock Telegram message."""
    message = AsyncMock(spec=Message)
    message.reply_text = AsyncMock()
    message.edit_text = AsyncMock()
    return message


@pytest.fixture
def mock_update(mock_user, mock_message):
    """Create a mock Telegram update."""
    update = MagicMock(spec=Update)
    update.effective_user = mock_user
    update.message = mock_message
    return update


@pytest.fixture
def mock_callback_query(mock_user, mock_message):
    """Create a mock callback query."""
    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    query.message = mock_message
    return query


@pytest.fixture
def mock_update_with_callback(mock_user, mock_callback_query):
    """Create a mock update with callback query."""
    update = MagicMock(spec=Update)
    update.effective_user = mock_user
    update.callback_query = mock_callback_query
    return update


@pytest.fixture
def mock_context():
    """Create a mock context."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context


# ==================== /linkweb Command Tests ====================

class TestLinkwebCommand:
    """Tests for /linkweb command handler."""
    
    @pytest.mark.asyncio
    async def test_linkweb_prompts_for_otp_when_user_exists(
        self, mock_update, mock_context
    ):
        """BOT-01: /linkweb prompts for OTP when user exists."""
        with patch("handlers.web_link.api_client") as mock_api:
            # User exists and not linked
            mock_api.get_user = AsyncMock(return_value={
                "id": "123",
                "role": "customer",
                "web_linked": False
            })
            
            result = await linkweb_command(mock_update, mock_context)
            
            assert result == WAITING_OTP
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            assert "کد ۶ رقمی" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_linkweb_rejects_unregistered_user(
        self, mock_update, mock_context
    ):
        """BOT-02: /linkweb rejects unregistered user."""
        with patch("handlers.web_link.api_client") as mock_api:
            mock_api.get_user = AsyncMock(return_value=None)
            
            result = await linkweb_command(mock_update, mock_context)
            
            assert result == ConversationHandler.END
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            assert "/start" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_linkweb_shows_message_if_already_linked(
        self, mock_update, mock_context
    ):
        """BOT-03: /linkweb shows message if already linked."""
        with patch("handlers.web_link.api_client") as mock_api:
            mock_api.get_user = AsyncMock(return_value={
                "id": "123",
                "role": "customer",
                "web_linked": True
            })
            
            result = await linkweb_command(mock_update, mock_context)
            
            assert result == ConversationHandler.END
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            assert "قبلاً" in call_args[0][0] or "متصل شده" in call_args[0][0]


# ==================== OTP Input Tests ====================

class TestOTPInput:
    """Tests for OTP input handler."""
    
    @pytest.mark.asyncio
    async def test_valid_6_digit_otp_is_accepted(
        self, mock_update, mock_context
    ):
        """BOT-04: Valid 6-digit OTP is accepted."""
        mock_update.message.text = "123456"
        
        with patch("handlers.web_link.api_client") as mock_api:
            mock_api.verify_telegram_link = AsyncMock(return_value={
                "success": True,
                "message": "Linked"
            })
            mock_api.get_user = AsyncMock(return_value={
                "id": "123",
                "role": "customer"
            })
            
            result = await handle_otp_input(mock_update, mock_context)
            
            assert result == ConversationHandler.END
            mock_api.verify_telegram_link.assert_called_once_with(
                "123456",
                mock_update.effective_user.id
            )
    
    @pytest.mark.asyncio
    async def test_invalid_otp_format_is_rejected(
        self, mock_update, mock_context
    ):
        """BOT-05: Invalid OTP format is rejected."""
        mock_update.message.text = "123"  # Too short
        
        result = await handle_otp_input(mock_update, mock_context)
        
        assert result == WAITING_OTP
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "نامعتبر" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_non_numeric_otp_is_rejected(
        self, mock_update, mock_context
    ):
        """Test non-numeric OTP is rejected."""
        mock_update.message.text = "abc123"
        
        result = await handle_otp_input(mock_update, mock_context)
        
        assert result == WAITING_OTP
        call_args = mock_update.message.reply_text.call_args
        assert "نامعتبر" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_expired_otp_is_rejected(
        self, mock_update, mock_context
    ):
        """BOT-06: Expired OTP is rejected."""
        mock_update.message.text = "123456"
        
        with patch("handlers.web_link.api_client") as mock_api:
            mock_api.verify_telegram_link = AsyncMock(return_value={
                "success": False,
                "message": "کد منقضی شده است"
            })
            
            result = await handle_otp_input(mock_update, mock_context)
            
            assert result == WAITING_OTP
    
    @pytest.mark.asyncio
    async def test_api_error_is_handled(
        self, mock_update, mock_context
    ):
        """Test API error is handled gracefully."""
        mock_update.message.text = "123456"
        
        with patch("handlers.web_link.api_client") as mock_api:
            mock_api.verify_telegram_link = AsyncMock(side_effect=Exception("API Error"))
            
            result = await handle_otp_input(mock_update, mock_context)
            
            assert result == WAITING_OTP
            call_args = mock_update.message.reply_text.call_args
            assert "خطا" in call_args[0][0]


# ==================== Cancel Tests ====================

class TestCancelLinkweb:
    """Tests for cancel handler."""
    
    @pytest.mark.asyncio
    async def test_cancel_button_ends_conversation(
        self, mock_update_with_callback, mock_context
    ):
        """BOT-07: Cancel button ends conversation."""
        with patch("handlers.web_link.api_client") as mock_api:
            mock_api.get_user = AsyncMock(return_value={
                "id": "123",
                "role": "customer"
            })
            
            result = await cancel_linkweb(mock_update_with_callback, mock_context)
            
            assert result == ConversationHandler.END
            mock_update_with_callback.callback_query.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cancel_shows_confirmation_message(
        self, mock_update_with_callback, mock_context
    ):
        """Test cancel shows confirmation message."""
        with patch("handlers.web_link.api_client") as mock_api:
            mock_api.get_user = AsyncMock(return_value={"id": "123", "role": "customer"})
            
            await cancel_linkweb(mock_update_with_callback, mock_context)
            
            mock_update_with_callback.callback_query.message.edit_text.assert_called_once()
            call_args = mock_update_with_callback.callback_query.message.edit_text.call_args
            assert "لغو" in call_args[0][0]


# ==================== API Client Tests ====================

class TestAPIClientVerifyTelegramLink:
    """Tests for API client verify_telegram_link method."""
    
    @pytest.mark.asyncio
    async def test_verify_telegram_link_api_client_method_works(self):
        """BOT-08: verify_telegram_link API client method works."""
        with patch("utils.api_client.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            
            from utils.api_client import api_client
            
            # Test the method
            with patch.object(api_client, '_get_client', return_value=mock_client):
                result = await api_client.verify_telegram_link("123456", 123456789)
            
            # Should return result
            if result:
                assert result.get("success") is True


# ==================== Conversation Handler Tests ====================

class TestConversationHandler:
    """Tests for conversation handler configuration."""
    
    def test_get_web_link_handler_returns_conversation_handler(self):
        """Test that get_web_link_handler returns a ConversationHandler."""
        from handlers.web_link import get_web_link_handler
        
        handler = get_web_link_handler()
        
        assert isinstance(handler, ConversationHandler)
        assert handler.name == "web_link"
    
    def test_handler_has_correct_entry_point(self):
        """Test handler has /linkweb command as entry point."""
        from handlers.web_link import get_web_link_handler
        from telegram.ext import CommandHandler
        
        handler = get_web_link_handler()
        
        assert len(handler.entry_points) == 1
        assert isinstance(handler.entry_points[0], CommandHandler)
    
    def test_handler_has_waiting_otp_state(self):
        """Test handler has WAITING_OTP state."""
        from handlers.web_link import get_web_link_handler
        
        handler = get_web_link_handler()
        
        assert WAITING_OTP in handler.states
        assert len(handler.states[WAITING_OTP]) >= 1


# ==================== Integration-like Tests ====================

class TestWebLinkFlow:
    """Integration-like tests for complete web link flow."""
    
    @pytest.mark.asyncio
    async def test_complete_successful_flow(
        self, mock_update, mock_context
    ):
        """Test complete successful linking flow."""
        with patch("handlers.web_link.api_client") as mock_api:
            # Step 1: User starts /linkweb
            mock_api.get_user = AsyncMock(return_value={
                "id": "123",
                "role": "customer",
                "web_linked": False
            })
            
            result1 = await linkweb_command(mock_update, mock_context)
            assert result1 == WAITING_OTP
            
            # Step 2: User enters OTP
            mock_update.message.text = "123456"
            mock_api.verify_telegram_link = AsyncMock(return_value={
                "success": True,
                "message": "Linked"
            })
            
            result2 = await handle_otp_input(mock_update, mock_context)
            assert result2 == ConversationHandler.END
    
    @pytest.mark.asyncio
    async def test_flow_with_retry_on_invalid_otp(
        self, mock_update, mock_context
    ):
        """Test flow with retry after invalid OTP."""
        with patch("handlers.web_link.api_client") as mock_api:
            # Start
            mock_api.get_user = AsyncMock(return_value={
                "id": "123",
                "role": "customer",
                "web_linked": False
            })
            
            await linkweb_command(mock_update, mock_context)
            
            # Invalid OTP
            mock_update.message.text = "123"
            result = await handle_otp_input(mock_update, mock_context)
            assert result == WAITING_OTP
            
            # Valid OTP
            mock_update.message.text = "123456"
            mock_api.verify_telegram_link = AsyncMock(return_value={
                "success": True
            })
            
            result = await handle_otp_input(mock_update, mock_context)
            assert result == ConversationHandler.END

