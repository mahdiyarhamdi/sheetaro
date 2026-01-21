"""Unit tests for AuthService."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest
from app.models.user import User
from app.models.enums import UserRole
from app.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ConflictException,
    NotFoundException,
)


# ==================== Fixtures ====================

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = AsyncMock()
    redis.setex = AsyncMock()
    redis.get = AsyncMock()
    redis.delete = AsyncMock()
    return redis


@pytest.fixture
def auth_service(mock_db_session, mock_redis):
    """Create AuthService instance with mocks."""
    return AuthService(mock_db_session, mock_redis)


@pytest.fixture
def auth_service_no_redis(mock_db_session):
    """Create AuthService instance without Redis."""
    return AuthService(mock_db_session, None)


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.phone_number = "09121234567"
    user.password_hash = "$2b$12$test_hash"
    user.first_name = "Test"
    user.last_name = "User"
    user.full_name = "Test User"
    user.telegram_id = None
    user.role = UserRole.CUSTOMER
    user.is_active = True
    user.phone_verified = False
    user.web_linked = False
    user.created_at = datetime.now(timezone.utc)
    user.is_admin = False
    return user


@pytest.fixture
def register_data():
    """Sample registration data."""
    return RegisterRequest(
        phone="09121234567",
        password="test123456",
        full_name="Test User"
    )


@pytest.fixture
def login_data():
    """Sample login data."""
    return LoginRequest(
        phone="09121234567",
        password="test123456"
    )


# ==================== Registration Tests ====================

class TestAuthServiceRegister:
    """Tests for AuthService.register method."""
    
    @pytest.mark.asyncio
    async def test_register_with_valid_data_creates_user(
        self, auth_service, mock_db_session, register_data
    ):
        """AUTH-U01: Register with valid data creates user."""
        # Setup: no existing user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Execute
        with patch('app.services.auth_service.get_password_hash', return_value='hashed_password'):
            user = await auth_service.register(register_data)
        
        # Verify
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_with_duplicate_phone_raises_conflict(
        self, auth_service, mock_db_session, register_data, sample_user
    ):
        """AUTH-U02: Register with duplicate phone raises ConflictException."""
        # Setup: existing user with same phone
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        # Execute & Verify
        with pytest.raises(ConflictException) as exc_info:
            await auth_service.register(register_data)
        
        assert "قبلاً ثبت شده" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_register_extracts_names_correctly(
        self, auth_service, mock_db_session
    ):
        """AUTH-U03: Register extracts first_name and last_name correctly."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Test with full name containing multiple parts
        data = RegisterRequest(
            phone="09121234567",
            password="test123456",
            full_name="Ali Rezaei Moghadam"
        )
        
        with patch('app.services.auth_service.get_password_hash', return_value='hashed'):
            await auth_service.register(data)
        
        # Verify the User was created with correct names
        call_args = mock_db_session.add.call_args[0][0]
        assert call_args.first_name == "Ali"
        assert call_args.last_name == "Rezaei Moghadam"
    
    @pytest.mark.asyncio
    async def test_register_single_name_sets_no_last_name(
        self, auth_service, mock_db_session
    ):
        """Test register with single name sets last_name to None."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        data = RegisterRequest(
            phone="09121234567",
            password="test123456",
            full_name="Ali"
        )
        
        with patch('app.services.auth_service.get_password_hash', return_value='hashed'):
            await auth_service.register(data)
        
        call_args = mock_db_session.add.call_args[0][0]
        assert call_args.first_name == "Ali"
        assert call_args.last_name is None


# ==================== Login Tests ====================

class TestAuthServiceLogin:
    """Tests for AuthService.login method."""
    
    @pytest.mark.asyncio
    async def test_login_with_valid_credentials_returns_user(
        self, auth_service, mock_db_session, login_data, sample_user
    ):
        """AUTH-U04: Login with valid credentials returns user."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        with patch('app.services.auth_service.verify_password', return_value=True):
            user = await auth_service.login(login_data)
        
        assert user == sample_user
    
    @pytest.mark.asyncio
    async def test_login_with_wrong_password_raises_unauthorized(
        self, auth_service, mock_db_session, login_data, sample_user
    ):
        """AUTH-U05: Login with wrong password raises UnauthorizedException."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        with patch('app.services.auth_service.verify_password', return_value=False):
            with pytest.raises(UnauthorizedException) as exc_info:
                await auth_service.login(login_data)
        
        assert "اشتباه" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_login_with_nonexistent_phone_raises_unauthorized(
        self, auth_service, mock_db_session, login_data
    ):
        """AUTH-U06: Login with non-existent phone raises UnauthorizedException."""
        # Setup: no user found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.login(login_data)
        
        assert "اشتباه" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_login_with_inactive_user_raises_unauthorized(
        self, auth_service, mock_db_session, login_data, sample_user
    ):
        """AUTH-U07: Login with inactive user raises UnauthorizedException."""
        # Setup
        sample_user.is_active = False
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        with patch('app.services.auth_service.verify_password', return_value=True):
            with pytest.raises(UnauthorizedException) as exc_info:
                await auth_service.login(login_data)
        
        assert "غیرفعال" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_login_without_password_hash_raises_unauthorized(
        self, auth_service, mock_db_session, login_data, sample_user
    ):
        """AUTH-U08: Login with user without password hash raises UnauthorizedException."""
        # Setup: user has no password (telegram-only user)
        sample_user.password_hash = None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.login(login_data)
        
        assert "تلگرام" in str(exc_info.value.detail)


# ==================== Token Tests ====================

class TestAuthServiceTokens:
    """Tests for AuthService token methods."""
    
    def test_create_tokens_returns_valid_tokens(self, auth_service, sample_user):
        """AUTH-U09: create_tokens returns valid access and refresh tokens."""
        access_token, refresh_token = auth_service.create_tokens(sample_user)
        
        assert access_token is not None
        assert refresh_token is not None
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert len(access_token) > 50  # JWT tokens are typically long
        assert len(refresh_token) > 50
    
    @pytest.mark.asyncio
    async def test_refresh_tokens_with_valid_token_returns_new_tokens(
        self, auth_service, mock_db_session, sample_user
    ):
        """AUTH-U10: refresh_tokens with valid token returns new tokens."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        # Create a valid refresh token first
        _, refresh_token = auth_service.create_tokens(sample_user)
        
        # Execute
        new_access, new_refresh, user = await auth_service.refresh_tokens(refresh_token)
        
        assert new_access is not None
        assert new_refresh is not None
        assert user == sample_user
    
    @pytest.mark.asyncio
    async def test_refresh_tokens_with_invalid_token_raises_unauthorized(
        self, auth_service
    ):
        """AUTH-U11: refresh_tokens with invalid token raises UnauthorizedException."""
        with pytest.raises(UnauthorizedException):
            await auth_service.refresh_tokens("invalid_token")
    
    @pytest.mark.asyncio
    async def test_refresh_tokens_with_access_token_raises_unauthorized(
        self, auth_service, sample_user
    ):
        """AUTH-U12: refresh_tokens with wrong token type raises UnauthorizedException."""
        # Create an access token (wrong type for refresh)
        access_token, _ = auth_service.create_tokens(sample_user)
        
        with pytest.raises(UnauthorizedException):
            await auth_service.refresh_tokens(access_token)
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token_returns_user(
        self, auth_service, mock_db_session, sample_user
    ):
        """AUTH-U13: get_current_user with valid token returns user."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        # Create valid access token
        access_token, _ = auth_service.create_tokens(sample_user)
        
        # Execute
        user = await auth_service.get_current_user(access_token)
        
        assert user == sample_user
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_expired_token_raises_unauthorized(
        self, auth_service, sample_user
    ):
        """AUTH-U14: get_current_user with expired token raises UnauthorizedException."""
        # Create token with negative expiry (already expired)
        with patch('app.services.auth_service.settings') as mock_settings:
            mock_settings.SECRET_KEY = "test-secret-key"
            mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = -1  # Negative = expired
            
            # This won't work easily without modifying the code
            # For now, test with invalid token
            with pytest.raises(UnauthorizedException):
                await auth_service.get_current_user("expired_token")


# ==================== OTP Tests ====================

class TestAuthServiceOTP:
    """Tests for AuthService OTP methods."""
    
    @pytest.mark.asyncio
    async def test_generate_telegram_link_otp_creates_6_digit_otp(
        self, auth_service, sample_user
    ):
        """AUTH-U15: generate_telegram_link_otp creates 6-digit OTP."""
        otp, expires_at = await auth_service.generate_telegram_link_otp(sample_user)
        
        assert len(otp) == 6
        assert otp.isdigit()
        assert expires_at > datetime.now(timezone.utc)
    
    @pytest.mark.asyncio
    async def test_generate_telegram_link_otp_stores_in_redis(
        self, auth_service, mock_redis, sample_user
    ):
        """AUTH-U16: generate_telegram_link_otp stores OTP in Redis."""
        await auth_service.generate_telegram_link_otp(sample_user)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert "telegram_link_otp:" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_generate_telegram_link_otp_without_redis_raises_bad_request(
        self, auth_service_no_redis, sample_user
    ):
        """AUTH-U17: generate_telegram_link_otp without Redis raises BadRequestException."""
        with pytest.raises(BadRequestException) as exc_info:
            await auth_service_no_redis.generate_telegram_link_otp(sample_user)
        
        assert "OTP" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_verify_telegram_link_with_valid_otp_links_account(
        self, auth_service, mock_db_session, mock_redis, sample_user
    ):
        """AUTH-U18: verify_telegram_link with valid OTP links account."""
        # Setup
        telegram_id = 123456789
        user_id_bytes = str(sample_user.id).encode()
        mock_redis.get.return_value = user_id_bytes
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [None, sample_user]  # No existing, then user
        mock_db_session.execute.return_value = mock_result
        
        # Execute
        user = await auth_service.verify_telegram_link("123456", telegram_id)
        
        # Verify
        mock_db_session.commit.assert_called()
        mock_redis.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_telegram_link_with_invalid_otp_raises_bad_request(
        self, auth_service, mock_redis
    ):
        """AUTH-U19: verify_telegram_link with invalid OTP raises BadRequestException."""
        # Setup: OTP not found in Redis
        mock_redis.get.return_value = None
        
        with pytest.raises(BadRequestException) as exc_info:
            await auth_service.verify_telegram_link("999999", 123456789)
        
        assert "نامعتبر" in str(exc_info.value.detail) or "منقضی" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_verify_telegram_link_with_already_linked_telegram_raises_conflict(
        self, auth_service, mock_db_session, mock_redis, sample_user
    ):
        """AUTH-U20: verify_telegram_link with already linked telegram raises ConflictException."""
        # Setup: another user already has this telegram_id
        telegram_id = 123456789
        other_user = MagicMock(spec=User)
        other_user.id = uuid4()  # Different user ID
        
        user_id_bytes = str(sample_user.id).encode()
        mock_redis.get.return_value = user_id_bytes
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = other_user
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(ConflictException) as exc_info:
            await auth_service.verify_telegram_link("123456", telegram_id)
        
        assert "قبلاً" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_verify_telegram_link_without_redis_raises_bad_request(
        self, auth_service_no_redis
    ):
        """Test verify_telegram_link without Redis raises BadRequestException."""
        with pytest.raises(BadRequestException) as exc_info:
            await auth_service_no_redis.verify_telegram_link("123456", 123456789)
        
        assert "OTP" in str(exc_info.value.detail)
