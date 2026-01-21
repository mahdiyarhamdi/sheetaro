"""Integration tests for Auth API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_test_web_user


# ==================== Registration Tests ====================

class TestAuthRegisterAPI:
    """Integration tests for POST /api/v1/auth/register endpoint."""
    
    @pytest.mark.asyncio
    async def test_register_with_valid_data_returns_201(
        self, client: AsyncClient, sample_web_user_data
    ):
        """AUTH-I01: POST /auth/register with valid data returns 201 and tokens."""
        response = await client.post(
            "/api/v1/auth/register",
            json=sample_web_user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["phone"] == sample_web_user_data["phone"]
        assert data["user"]["full_name"] == sample_web_user_data["full_name"]
    
    @pytest.mark.asyncio
    async def test_register_with_invalid_phone_returns_422(
        self, client: AsyncClient
    ):
        """AUTH-I02: POST /auth/register with invalid phone returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "phone": "12345",  # Invalid phone
                "password": "test123456",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_with_short_password_returns_422(
        self, client: AsyncClient
    ):
        """AUTH-I03: POST /auth/register with short password returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "phone": "09121234567",
                "password": "12345",  # Too short (min 6)
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_with_duplicate_phone_returns_409(
        self, client: AsyncClient, sample_web_user_data
    ):
        """AUTH-I04: POST /auth/register with duplicate phone returns 409."""
        # First registration
        await client.post("/api/v1/auth/register", json=sample_web_user_data)
        
        # Second registration with same phone
        response = await client.post(
            "/api/v1/auth/register",
            json=sample_web_user_data
        )
        
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_register_normalizes_phone_format(
        self, client: AsyncClient
    ):
        """Test register normalizes different phone formats."""
        # Test with 98 prefix
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "phone": "989121234567",
                "password": "test123456",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 201
        assert response.json()["user"]["phone"] == "09121234567"


# ==================== Login Tests ====================

class TestAuthLoginAPI:
    """Integration tests for POST /api/v1/auth/login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_with_valid_credentials_returns_200(
        self, client: AsyncClient, sample_web_user_data
    ):
        """AUTH-I05: POST /auth/login with valid credentials returns 200 and tokens."""
        # First register
        await client.post("/api/v1/auth/register", json=sample_web_user_data)
        
        # Then login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": sample_web_user_data["phone"],
                "password": sample_web_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
    
    @pytest.mark.asyncio
    async def test_login_with_wrong_password_returns_401(
        self, client: AsyncClient, sample_web_user_data
    ):
        """AUTH-I06: POST /auth/login with wrong password returns 401."""
        # First register
        await client.post("/api/v1/auth/register", json=sample_web_user_data)
        
        # Login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": sample_web_user_data["phone"],
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_with_nonexistent_user_returns_401(
        self, client: AsyncClient
    ):
        """AUTH-I07: POST /auth/login with non-existent user returns 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": "09999999999",
                "password": "any_password"
            }
        )
        
        assert response.status_code == 401


# ==================== Token Refresh Tests ====================

class TestAuthRefreshAPI:
    """Integration tests for POST /api/v1/auth/refresh endpoint."""
    
    @pytest.mark.asyncio
    async def test_refresh_with_valid_token_returns_new_tokens(
        self, client: AsyncClient, sample_web_user_data
    ):
        """AUTH-I08: POST /auth/refresh with valid token returns new tokens."""
        # Register and get tokens
        register_response = await client.post(
            "/api/v1/auth/register",
            json=sample_web_user_data
        )
        refresh_token = register_response.json()["refresh_token"]
        
        # Refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"] != register_response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token_returns_401(
        self, client: AsyncClient
    ):
        """AUTH-I09: POST /auth/refresh with invalid token returns 401."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401


# ==================== Get Current User Tests ====================

class TestAuthMeAPI:
    """Integration tests for GET /api/v1/auth/me endpoint."""
    
    @pytest.mark.asyncio
    async def test_me_with_valid_token_returns_user(
        self, client: AsyncClient, authenticated_user, auth_headers
    ):
        """AUTH-I10: GET /auth/me with valid token returns user."""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "phone" in data
        assert "full_name" in data
    
    @pytest.mark.asyncio
    async def test_me_without_token_returns_401(
        self, client: AsyncClient
    ):
        """AUTH-I11: GET /auth/me without token returns 401."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_me_with_malformed_token_returns_401(
        self, client: AsyncClient
    ):
        """AUTH-I12: GET /auth/me with malformed token returns 401."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_me_with_wrong_auth_format_returns_401(
        self, client: AsyncClient, authenticated_user
    ):
        """Test /auth/me with wrong auth format returns 401."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Basic {authenticated_user['access_token']}"}
        )
        
        assert response.status_code == 401


# ==================== Telegram Link Tests ====================

class TestAuthTelegramLinkAPI:
    """Integration tests for Telegram account linking endpoints."""
    
    @pytest.mark.asyncio
    async def test_telegram_link_returns_otp(
        self, client: AsyncClient, authenticated_user, auth_headers
    ):
        """AUTH-I13: POST /auth/telegram-link returns OTP and expires_at."""
        response = await client.post(
            "/api/v1/auth/telegram-link",
            headers=auth_headers
        )
        
        # May return 400 if Redis is not available in test environment
        if response.status_code == 200:
            data = response.json()
            assert "otp" in data
            assert "expires_at" in data
            assert len(data["otp"]) == 6
            assert data["otp"].isdigit()
        else:
            # Accept 400 if OTP service unavailable
            assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_telegram_link_without_auth_returns_401(
        self, client: AsyncClient
    ):
        """Test /auth/telegram-link without auth returns 401."""
        response = await client.post("/api/v1/auth/telegram-link")
        
        assert response.status_code == 401


class TestAuthTelegramVerifyAPI:
    """Integration tests for Telegram verification endpoint."""
    
    @pytest.mark.asyncio
    async def test_telegram_verify_with_invalid_otp_returns_400(
        self, client: AsyncClient
    ):
        """AUTH-I15: POST /auth/telegram-verify with invalid OTP returns 400."""
        response = await client.post(
            "/api/v1/auth/telegram-verify",
            json={"otp": "999999"},
            headers={"X-Telegram-ID": "123456789"}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_telegram_verify_without_telegram_id_returns_422(
        self, client: AsyncClient
    ):
        """AUTH-I16: POST /auth/telegram-verify without X-Telegram-ID returns 422."""
        response = await client.post(
            "/api/v1/auth/telegram-verify",
            json={"otp": "123456"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_telegram_verify_with_short_otp_returns_422(
        self, client: AsyncClient
    ):
        """Test /auth/telegram-verify with short OTP returns 422."""
        response = await client.post(
            "/api/v1/auth/telegram-verify",
            json={"otp": "123"},  # Too short
            headers={"X-Telegram-ID": "123456789"}
        )
        
        assert response.status_code == 422


# ==================== Edge Cases ====================

class TestAuthEdgeCases:
    """Edge case tests for Auth API."""
    
    @pytest.mark.asyncio
    async def test_register_with_empty_name_returns_422(
        self, client: AsyncClient
    ):
        """Test register with empty name returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "phone": "09121234567",
                "password": "test123456",
                "full_name": ""  # Empty
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_with_missing_fields_returns_422(
        self, client: AsyncClient
    ):
        """Test register with missing fields returns 422."""
        # Missing password
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "phone": "09121234567",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_login_with_empty_fields_returns_422(
        self, client: AsyncClient
    ):
        """Test login with empty fields returns 422."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": "",
                "password": ""
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_multiple_logins_return_different_tokens(
        self, client: AsyncClient, sample_web_user_data
    ):
        """Test multiple logins return different tokens."""
        # Register
        await client.post("/api/v1/auth/register", json=sample_web_user_data)
        
        # Login twice
        login1 = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": sample_web_user_data["phone"],
                "password": sample_web_user_data["password"]
            }
        )
        
        login2 = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": sample_web_user_data["phone"],
                "password": sample_web_user_data["password"]
            }
        )
        
        assert login1.json()["access_token"] != login2.json()["access_token"]

