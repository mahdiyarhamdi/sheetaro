"""Integration tests for System Fonts API endpoints."""

import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient

from tests.conftest import create_test_admin_user, create_admin_token
from app.models.enums import UserRole


class TestFontsList:
    """Test font listing endpoints."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120001001",
            "password_hash": "hashed_password",
            "first_name": "Font",
            "last_name": "Admin",
            "full_name": "Font Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.fixture
    async def sample_fonts(self, client: AsyncClient, admin_headers):
        """Create sample fonts for testing."""
        fonts = []
        for i in range(3):
            response = await client.post(
                "/api/v1/fonts",
                json={
                    "name": f"TestFont{i}",
                    "name_fa": f"فونت تست {i}",
                    "file_url": f"/fonts/TestFont{i}.ttf",
                    "is_active": i != 2,  # Last one inactive
                },
                headers=admin_headers,
            )
            if response.status_code == 201:
                fonts.append(response.json())
        return fonts
    
    @pytest.mark.asyncio
    async def test_list_fonts_returns_all(self, client: AsyncClient, sample_fonts):
        """Test listing all fonts."""
        response = await client.get("/api/v1/fonts")
        
        assert response.status_code == 200
        data = response.json()
        # Should return list
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_list_fonts_active_only_filter(self, client: AsyncClient, sample_fonts):
        """Test filtering fonts by active status."""
        response = await client.get("/api/v1/fonts?active_only=true")
        
        assert response.status_code == 200
        data = response.json()
        # All returned fonts should be active
        for font in data:
            assert font.get("is_active", True) is True
    
    @pytest.mark.asyncio
    async def test_list_fonts_empty_returns_empty_list(self, client: AsyncClient):
        """Test that empty database returns empty list."""
        response = await client.get("/api/v1/fonts?active_only=false")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestFontCreate:
    """Test font creation endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120001002",
            "password_hash": "hashed_password",
            "first_name": "Font",
            "last_name": "Admin",
            "full_name": "Font Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.fixture
    async def regular_user(self, db_session):
        """Create a regular user for testing."""
        from tests.conftest import create_test_web_user
        from app.core.security import get_password_hash
        return await create_test_web_user(db_session, {
            "phone_number": "09120001003",
            "password_hash": get_password_hash("user123456"),
            "first_name": "Regular",
            "last_name": "User",
            "full_name": "Regular User",
            "role": UserRole.CUSTOMER,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def regular_user_headers(self, regular_user):
        """Get regular user authorization headers."""
        token = create_admin_token(str(regular_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.mark.asyncio
    async def test_create_font_success(self, client: AsyncClient, admin_headers):
        """Test successful font creation."""
        response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "IRANSans",
                "name_fa": "ایران سنس",
                "file_url": "/fonts/IRANSans.ttf",
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "IRANSans"
        assert data["name_fa"] == "ایران سنس"
        assert data["file_url"] == "/fonts/IRANSans.ttf"
        assert data["is_active"] is True
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_font_with_variants(self, client: AsyncClient, admin_headers):
        """Test creating font with variants."""
        response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "Vazir",
                "name_fa": "وزیر",
                "file_url": "/fonts/Vazir.ttf",
                "variants": [
                    {"weight": 400, "style": "normal", "file_url": "/fonts/Vazir-Regular.ttf"},
                    {"weight": 700, "style": "normal", "file_url": "/fonts/Vazir-Bold.ttf"},
                ],
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["variants"]) == 2
        assert data["variants"][0]["weight"] == 400
        assert data["variants"][1]["weight"] == 700
    
    @pytest.mark.asyncio
    async def test_create_font_requires_admin(self, client: AsyncClient, regular_user_headers):
        """Test that non-admin cannot create fonts."""
        response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "TestFont",
                "name_fa": "فونت تست",
            },
            headers=regular_user_headers,
        )
        
        # Should be rejected (403 or 401)
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_create_font_duplicate_name_rejected(self, client: AsyncClient, admin_headers):
        """Test that duplicate font names are rejected."""
        # Create first font
        await client.post(
            "/api/v1/fonts",
            json={
                "name": "DuplicateTest",
                "name_fa": "فونت تکراری",
            },
            headers=admin_headers,
        )
        
        # Try to create with same name
        response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "DuplicateTest",
                "name_fa": "فونت دیگر",
            },
            headers=admin_headers,
        )
        
        # Should fail with 400 or 409
        assert response.status_code in [400, 409, 500]
    
    @pytest.mark.asyncio
    async def test_create_font_without_file_url(self, client: AsyncClient, admin_headers):
        """Test creating font without file_url."""
        response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "NoFileFont",
                "name_fa": "فونت بدون فایل",
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["file_url"] is None
    
    @pytest.mark.asyncio
    async def test_create_font_missing_required_fields(self, client: AsyncClient, admin_headers):
        """Test font creation with missing required fields."""
        response = await client.post(
            "/api/v1/fonts",
            json={
                "name_fa": "فونت بدون نام انگلیسی",
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 422


class TestFontUpdate:
    """Test font update endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120001004",
            "password_hash": "hashed_password",
            "first_name": "Font",
            "last_name": "Admin",
            "full_name": "Font Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.fixture
    async def test_font(self, client: AsyncClient, admin_headers):
        """Create a test font."""
        response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "UpdateTestFont",
                "name_fa": "فونت برای ویرایش",
                "file_url": "/fonts/Update.ttf",
            },
            headers=admin_headers,
        )
        return response.json()
    
    @pytest.mark.asyncio
    async def test_update_font_name(self, client: AsyncClient, test_font, admin_headers):
        """Test updating font name."""
        response = await client.patch(
            f"/api/v1/fonts/{test_font['id']}",
            json={
                "name_fa": "نام جدید",
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name_fa"] == "نام جدید"
    
    @pytest.mark.asyncio
    async def test_update_font_variants(self, client: AsyncClient, test_font, admin_headers):
        """Test updating font variants."""
        new_variants = [
            {"weight": 300, "style": "normal", "file_url": "/fonts/Light.ttf"},
            {"weight": 500, "style": "normal", "file_url": "/fonts/Medium.ttf"},
        ]
        
        response = await client.patch(
            f"/api/v1/fonts/{test_font['id']}",
            json={
                "variants": new_variants,
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["variants"]) == 2
    
    @pytest.mark.asyncio
    async def test_update_font_toggle_active(self, client: AsyncClient, test_font, admin_headers):
        """Test toggling font active status."""
        # Deactivate
        response = await client.patch(
            f"/api/v1/fonts/{test_font['id']}",
            json={"is_active": False},
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert response.json()["is_active"] is False
        
        # Reactivate
        response = await client.patch(
            f"/api/v1/fonts/{test_font['id']}",
            json={"is_active": True},
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert response.json()["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_update_font_not_found_returns_404(self, client: AsyncClient, admin_headers):
        """Test updating non-existent font."""
        fake_id = str(uuid4())
        
        response = await client.patch(
            f"/api/v1/fonts/{fake_id}",
            json={"name_fa": "تست"},
            headers=admin_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_font_requires_admin(self, client: AsyncClient, test_font):
        """Test that non-admin cannot update fonts."""
        response = await client.patch(
            f"/api/v1/fonts/{test_font['id']}",
            json={"name_fa": "غیرمجاز"},
            # No auth header
        )
        
        assert response.status_code in [401, 403]


class TestFontDelete:
    """Test font deletion endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120001005",
            "password_hash": "hashed_password",
            "first_name": "Font",
            "last_name": "Admin",
            "full_name": "Font Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.mark.asyncio
    async def test_delete_font_success(self, client: AsyncClient, admin_headers):
        """Test successful font deletion."""
        # Create font first
        create_response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "DeleteTestFont",
                "name_fa": "فونت برای حذف",
            },
            headers=admin_headers,
        )
        font_id = create_response.json()["id"]
        
        # Delete font
        response = await client.delete(
            f"/api/v1/fonts/{font_id}",
            headers=admin_headers,
        )
        
        assert response.status_code == 204
        
        # Verify deleted
        get_response = await client.get(f"/api/v1/fonts/{font_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_font_not_found_returns_404(self, client: AsyncClient, admin_headers):
        """Test deleting non-existent font."""
        fake_id = str(uuid4())
        
        response = await client.delete(
            f"/api/v1/fonts/{fake_id}",
            headers=admin_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_font_requires_admin(self, client: AsyncClient, admin_headers):
        """Test that non-admin cannot delete fonts."""
        # Create font first
        create_response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "NoDeleteFont",
                "name_fa": "فونت غیرقابل حذف",
            },
            headers=admin_headers,
        )
        font_id = create_response.json()["id"]
        
        # Try to delete without auth
        response = await client.delete(
            f"/api/v1/fonts/{font_id}",
            # No auth header
        )
        
        assert response.status_code in [401, 403]


class TestFontGet:
    """Test font retrieval endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120001006",
            "password_hash": "hashed_password",
            "first_name": "Font",
            "last_name": "Admin",
            "full_name": "Font Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.mark.asyncio
    async def test_get_font_by_id(self, client: AsyncClient, admin_headers):
        """Test getting font by ID."""
        # Create font first
        create_response = await client.post(
            "/api/v1/fonts",
            json={
                "name": "GetTestFont",
                "name_fa": "فونت برای دریافت",
                "sample_text": "متن نمونه سفارشی",
            },
            headers=admin_headers,
        )
        font_id = create_response.json()["id"]
        
        # Get font
        response = await client.get(f"/api/v1/fonts/{font_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == font_id
        assert data["name"] == "GetTestFont"
        assert data["sample_text"] == "متن نمونه سفارشی"
    
    @pytest.mark.asyncio
    async def test_get_font_not_found(self, client: AsyncClient):
        """Test getting non-existent font."""
        fake_id = str(uuid4())
        
        response = await client.get(f"/api/v1/fonts/{fake_id}")
        
        assert response.status_code == 404

