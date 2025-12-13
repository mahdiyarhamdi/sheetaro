"""Integration tests for Users API."""

import pytest
from httpx import AsyncClient


class TestUsersAPI:
    """Integration tests for /api/v1/users endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, sample_user_data):
        """Test POST /api/v1/users - create new user."""
        response = await client.post("/api/v1/users", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["telegram_id"] == sample_user_data["telegram_id"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_create_user_updates_existing(self, client: AsyncClient, sample_user_data):
        """Test POST /api/v1/users - updates existing user."""
        # Create user
        response1 = await client.post("/api/v1/users", json=sample_user_data)
        assert response1.status_code == 201
        user_id = response1.json()["id"]
        
        # Update user (same telegram_id)
        sample_user_data["first_name"] = "Updated"
        response2 = await client.post("/api/v1/users", json=sample_user_data)
        
        assert response2.status_code == 201
        data = response2.json()
        assert data["id"] == user_id  # Same user
        assert data["first_name"] == "Updated"
    
    @pytest.mark.asyncio
    async def test_get_user(self, client: AsyncClient, sample_user_data):
        """Test GET /api/v1/users/{telegram_id}."""
        # Create user first
        await client.post("/api/v1/users", json=sample_user_data)
        
        # Get user
        response = await client.get(f"/api/v1/users/{sample_user_data['telegram_id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == sample_user_data["telegram_id"]
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient):
        """Test GET /api/v1/users/{telegram_id} - not found."""
        response = await client.get("/api/v1/users/999999999")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient, sample_user_data):
        """Test PATCH /api/v1/users/{telegram_id}."""
        # Create user first
        await client.post("/api/v1/users", json=sample_user_data)
        
        # Update user
        update_data = {"first_name": "NewName", "city": "Mashhad"}
        response = await client.patch(
            f"/api/v1/users/{sample_user_data['telegram_id']}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "NewName"
        assert data["city"] == "Mashhad"
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client: AsyncClient):
        """Test PATCH /api/v1/users/{telegram_id} - not found."""
        update_data = {"first_name": "NewName"}
        response = await client.patch("/api/v1/users/999999999", json=update_data)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_phone(self, client: AsyncClient, sample_user_data):
        """Test POST /api/v1/users - invalid phone number."""
        sample_user_data["phone_number"] = "invalid"
        response = await client.post("/api/v1/users", json=sample_user_data)
        
        assert response.status_code == 422

