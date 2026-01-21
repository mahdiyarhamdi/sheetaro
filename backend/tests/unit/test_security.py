"""Unit tests for security module (password hashing and JWT)."""

import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.core.config import settings


# ==================== Password Hashing Tests ====================

class TestPasswordHashing:
    """Tests for password hashing functions."""
    
    def test_get_password_hash_returns_bcrypt_hash(self):
        """SEC-U01: get_password_hash returns bcrypt hash."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # bcrypt hashes start with $2b$ or $2a$
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
        assert len(hashed) == 60  # bcrypt hashes are 60 characters
    
    def test_verify_password_returns_true_for_correct_password(self):
        """SEC-U02: verify_password returns True for correct password."""
        password = "correct_password"
        hashed = get_password_hash(password)
        
        result = verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_returns_false_for_wrong_password(self):
        """SEC-U03: verify_password returns False for wrong password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_password_hash_is_different_each_time(self):
        """Test that same password produces different hashes (salt)."""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to random salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_empty_password_can_be_hashed(self):
        """Test that empty password can be hashed (though not recommended)."""
        password = ""
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed)
        assert not verify_password("nonempty", hashed)
    
    def test_unicode_password_can_be_hashed(self):
        """Test that unicode passwords work correctly."""
        password = "رمزعبورفارسی۱۲۳"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)
        assert not verify_password("wrong", hashed)
    
    def test_long_password_can_be_hashed(self):
        """Test that long passwords work correctly."""
        password = "a" * 100  # 100 character password
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)


# ==================== JWT Token Tests ====================

class TestJWTTokens:
    """Tests for JWT token functions."""
    
    def test_jwt_token_contains_correct_claims(self):
        """SEC-U04: JWT token contains correct claims (sub, type, exp)."""
        data = {"sub": "user_123", "type": "access"}
        token = create_access_token(data)
        
        # Decode and verify claims
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert payload["sub"] == "user_123"
        assert payload.get("type") == "access"
        assert "exp" in payload
    
    def test_jwt_token_is_verifiable(self):
        """SEC-U05: JWT token is verifiable with SECRET_KEY."""
        data = {"sub": "user_123"}
        token = create_access_token(data)
        
        # Should not raise an exception
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert payload["sub"] == "user_123"
    
    def test_jwt_token_with_custom_expiry(self):
        """Test JWT token with custom expiry time."""
        data = {"sub": "user_123"}
        expires_delta = timedelta(hours=2)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Check expiry is approximately 2 hours from now
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + expires_delta
        
        # Allow 5 seconds of tolerance
        assert abs((exp_datetime - expected_exp).total_seconds()) < 5
    
    def test_jwt_token_default_expiry(self):
        """Test JWT token with default 24 hour expiry."""
        data = {"sub": "user_123"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Allow 5 seconds of tolerance
        assert abs((exp_datetime - expected_exp).total_seconds()) < 5
    
    def test_jwt_token_with_additional_data(self):
        """Test JWT token preserves additional data."""
        data = {
            "sub": "user_123",
            "role": "admin",
            "custom_field": "custom_value"
        }
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert payload["sub"] == "user_123"
        assert payload["role"] == "admin"
        assert payload["custom_field"] == "custom_value"
    
    def test_jwt_token_invalid_with_wrong_key(self):
        """Test JWT token is invalid with wrong secret key."""
        data = {"sub": "user_123"}
        token = create_access_token(data)
        
        with pytest.raises(jwt.JWTError):
            jwt.decode(token, "wrong_secret_key", algorithms=["HS256"])
    
    def test_jwt_token_invalid_with_wrong_algorithm(self):
        """Test JWT token is invalid with wrong algorithm."""
        data = {"sub": "user_123"}
        token = create_access_token(data)
        
        with pytest.raises(jwt.JWTError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS384"])
    
    def test_jwt_token_expired_is_invalid(self):
        """Test that expired JWT token raises exception."""
        data = {"sub": "user_123"}
        # Create token that's already expired
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
