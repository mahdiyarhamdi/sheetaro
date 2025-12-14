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


class TestAdminManagementAPI:
    """Integration tests for admin management endpoints."""
    
    @pytest.fixture
    async def setup_admin(self, client: AsyncClient):
        """Create an admin user."""
        admin_data = {
            "telegram_id": 111111111,
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "role": "ADMIN",
        }
        response = await client.post("/api/v1/users", json=admin_data)
        return response.json()
    
    @pytest.fixture
    async def setup_regular_user(self, client: AsyncClient):
        """Create a regular user."""
        user_data = {
            "telegram_id": 222222222,
            "username": "regular",
            "first_name": "Regular",
            "last_name": "User",
            "role": "CUSTOMER",
        }
        response = await client.post("/api/v1/users", json=user_data)
        return response.json()
    
    @pytest.mark.asyncio
    async def test_get_admins_list(self, client: AsyncClient, setup_admin):
        """Test GET /api/v1/users/admins/list."""
        admin = await setup_admin
        
        response = await client.get(
            "/api/v1/users/admins/list",
            params={"admin_id": admin["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_admin_telegram_ids(self, client: AsyncClient, setup_admin):
        """Test GET /api/v1/users/admins/telegram-ids."""
        admin = await setup_admin
        
        response = await client.get("/api/v1/users/admins/telegram-ids")
        
        assert response.status_code == 200
        data = response.json()
        assert admin["telegram_id"] in data
    
    @pytest.mark.asyncio
    async def test_promote_to_admin(self, client: AsyncClient, setup_admin, setup_regular_user):
        """Test POST /api/v1/users/admins/promote."""
        admin = await setup_admin
        regular = await setup_regular_user
        
        promote_data = {"target_telegram_id": regular["telegram_id"]}
        response = await client.post(
            "/api/v1/users/admins/promote",
            json=promote_data,
            params={"admin_id": admin["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "ADMIN"
    
    @pytest.mark.asyncio
    async def test_promote_non_admin_fails(self, client: AsyncClient, setup_regular_user):
        """Test that non-admin cannot promote users."""
        regular = await setup_regular_user
        
        # Create another user to promote
        other_user_data = {
            "telegram_id": 333333333,
            "first_name": "Other",
            "role": "CUSTOMER",
        }
        await client.post("/api/v1/users", json=other_user_data)
        
        promote_data = {"target_telegram_id": 333333333}
        response = await client.post(
            "/api/v1/users/admins/promote",
            json=promote_data,
            params={"admin_id": regular["id"]}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_demote_from_admin(self, client: AsyncClient, setup_admin):
        """Test POST /api/v1/users/admins/demote."""
        admin = await setup_admin
        
        # Create another admin to demote
        other_admin_data = {
            "telegram_id": 444444444,
            "first_name": "OtherAdmin",
            "role": "ADMIN",
        }
        other_response = await client.post("/api/v1/users", json=other_admin_data)
        other_admin = other_response.json()
        
        demote_data = {"target_telegram_id": other_admin["telegram_id"]}
        response = await client.post(
            "/api/v1/users/admins/demote",
            json=demote_data,
            params={"admin_id": admin["id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "CUSTOMER"

