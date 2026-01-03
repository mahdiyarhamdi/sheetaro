"""Integration tests for Questions API endpoints."""

import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient

from tests.conftest import create_test_user
from app.models.enums import UserRole


class TestQuestionsAPI:
    """Comprehensive tests for questions API endpoints."""

    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        user = await create_test_user(
            db_session,
            {
                "telegram_id": 111222333,
                "username": "questionsadmin",
                "first_name": "Questions",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
            }
        )
        return user

    @pytest_asyncio.fixture
    async def test_category(self, client: AsyncClient, admin_user):
        """Create a test category."""
        response = await client.post(
            "/api/v1/categories",
            json={
                "name_fa": "لیبل سوالات",
                "name_en": "Question Labels",
                "slug": "question-labels",
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        return response.json()

    @pytest_asyncio.fixture
    async def test_plan(self, client: AsyncClient, test_category, admin_user):
        """Create a test design plan with questionnaire enabled."""
        response = await client.post(
            f"/api/v1/categories/{test_category['id']}/plans",
            json={
                "name_fa": "نیمه‌خصوصی",
                "slug": "semi-private",
                "plan_type": "SEMI_PRIVATE",
                "has_questionnaire": True,
                "has_templates": False,
                "price": 50000,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        return response.json()

    # ==================== Create Question Tests ====================

    @pytest.mark.asyncio
    async def test_create_question_text_type(self, client: AsyncClient, test_plan, admin_user):
        """Test creating a TEXT type question."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "نام برند خود را وارد کنید",
                "input_type": "TEXT",
                "is_required": True,
                "placeholder_fa": "مثال: برند من",
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["question_fa"] == "نام برند خود را وارد کنید"
        assert data["input_type"] == "TEXT"

    @pytest.mark.asyncio
    async def test_create_question_number_type(self, client: AsyncClient, test_plan, admin_user):
        """Test creating a NUMBER type question."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "تعداد مورد نیاز را وارد کنید",
                "input_type": "NUMBER",
                "is_required": True,
                "validation_rules": {
                    "min_value": 100,
                    "max_value": 10000,
                },
                "sort_order": 2,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["input_type"] == "NUMBER"

    @pytest.mark.asyncio
    async def test_create_question_single_choice(self, client: AsyncClient, test_plan, admin_user):
        """Test creating a SINGLE_CHOICE question with options."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "نوع جنس را انتخاب کنید",
                "input_type": "SINGLE_CHOICE",
                "is_required": True,
                "options": [
                    {"label_fa": "کاغذی", "value": "paper", "sort_order": 1},
                    {"label_fa": "پی وی سی", "value": "pvc", "price_modifier": 5000, "sort_order": 2},
                    {"label_fa": "متالیک", "value": "metallic", "price_modifier": 10000, "sort_order": 3},
                ],
                "sort_order": 3,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["input_type"] == "SINGLE_CHOICE"
        assert len(data.get("options", [])) >= 3

    @pytest.mark.asyncio
    async def test_create_question_multi_choice(self, client: AsyncClient, test_plan, admin_user):
        """Test creating a MULTI_CHOICE question."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "ویژگی‌های مورد نظر را انتخاب کنید",
                "input_type": "MULTI_CHOICE",
                "is_required": True,
                "validation_rules": {
                    "min_selections": 1,
                    "max_selections": 3,
                },
                "options": [
                    {"label_fa": "ضد آب", "value": "waterproof", "sort_order": 1},
                    {"label_fa": "براق", "value": "glossy", "sort_order": 2},
                    {"label_fa": "مات", "value": "matte", "sort_order": 3},
                ],
                "sort_order": 4,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["input_type"] == "MULTI_CHOICE"

    @pytest.mark.asyncio
    async def test_create_question_color_picker(self, client: AsyncClient, test_plan, admin_user):
        """Test creating a COLOR_PICKER type question."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "رنگ پس‌زمینه را انتخاب کنید",
                "input_type": "COLOR_PICKER",
                "is_required": False,
                "help_text_fa": "کد رنگ مانند #FF5733",
                "sort_order": 5,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["input_type"] == "COLOR_PICKER"

    @pytest.mark.asyncio
    async def test_create_question_image_upload(self, client: AsyncClient, test_plan, admin_user):
        """Test creating an IMAGE_UPLOAD type question."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "لوگوی برند خود را آپلود کنید",
                "input_type": "IMAGE_UPLOAD",
                "is_required": True,
                "validation_rules": {
                    "allowed_types": ["jpg", "jpeg", "png"],
                    "max_file_size_mb": 5,
                },
                "sort_order": 6,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["input_type"] == "IMAGE_UPLOAD"

    @pytest.mark.asyncio
    async def test_create_question_with_options(self, client: AsyncClient, test_plan, admin_user):
        """Test creating question with inline options."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "سایز لیبل را انتخاب کنید",
                "input_type": "SINGLE_CHOICE",
                "is_required": True,
                "options": [
                    {"label_fa": "۵×۵ سانتی", "value": "5x5"},
                    {"label_fa": "۱۰×۵ سانتی", "value": "10x5"},
                ],
                "sort_order": 7,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data.get("options", [])) == 2

    # ==================== Option Management Tests ====================

    @pytest.mark.asyncio
    async def test_add_option_to_question(self, client: AsyncClient, test_plan, admin_user):
        """Test adding an option to an existing question."""
        # Create question first
        question_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "رنگ را انتخاب کنید",
                "input_type": "SINGLE_CHOICE",
                "is_required": True,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        question_id = question_response.json()["id"]
        
        # Add option
        response = await client.post(
            f"/api/v1/questions/{question_id}/options",
            json={
                "label_fa": "قرمز",
                "value": "red",
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["value"] == "red"

    # ==================== Update and Delete Tests ====================

    @pytest.mark.asyncio
    async def test_update_question(self, client: AsyncClient, test_plan, admin_user):
        """Test updating a question."""
        # Create question
        create_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "سوال اولیه",
                "input_type": "TEXT",
                "is_required": True,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        question_id = create_response.json()["id"]
        
        # Update question
        response = await client.patch(
            f"/api/v1/questions/{question_id}",
            json={
                "question_fa": "سوال ویرایش شده",
                "is_required": False,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["question_fa"] == "سوال ویرایش شده"
        assert data["is_required"] is False

    @pytest.mark.asyncio
    async def test_delete_question(self, client: AsyncClient, test_plan, admin_user):
        """Test deleting a question."""
        # Create question
        create_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "سوال موقت",
                "input_type": "TEXT",
                "is_required": True,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        question_id = create_response.json()["id"]
        
        # Delete question
        response = await client.delete(
            f"/api/v1/questions/{question_id}",
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_list_questions_by_plan(self, client: AsyncClient, test_plan, admin_user):
        """Test listing questions for a plan."""
        # Create multiple questions
        for i in range(3):
            await client.post(
                f"/api/v1/plans/{test_plan['id']}/questions",
                json={
                    "question_fa": f"سوال {i + 1}",
                    "input_type": "TEXT",
                    "is_required": True,
                    "sort_order": i + 1,
                },
                headers={"X-Telegram-ID": str(admin_user.telegram_id)},
            )
        
        # List questions
        response = await client.get(
            f"/api/v1/plans/{test_plan['id']}/questions",
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    # ==================== Validation Tests ====================

    @pytest.mark.asyncio
    async def test_validate_answer_text_valid(self, client: AsyncClient, test_plan, admin_user):
        """Test validating a valid text answer."""
        # Create question with validation rules
        question_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "نام را وارد کنید",
                "input_type": "TEXT",
                "is_required": True,
                "validation_rules": {
                    "min_length": 2,
                    "max_length": 50,
                },
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        question_id = question_response.json()["id"]
        
        # Validate answer
        response = await client.post(
            f"/api/v1/questions/{question_id}/validate",
            json={
                "answer_text": "نام تست",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_answer_text_too_short(self, client: AsyncClient, test_plan, admin_user):
        """Test validating a text answer that's too short."""
        question_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "نام را وارد کنید",
                "input_type": "TEXT",
                "is_required": True,
                "validation_rules": {
                    "min_length": 5,
                },
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        question_id = question_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/questions/{question_id}/validate",
            json={
                "answer_text": "آ",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "error_message" in data

    @pytest.mark.asyncio
    async def test_validate_answer_number_valid(self, client: AsyncClient, test_plan, admin_user):
        """Test validating a valid number answer."""
        question_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "تعداد را وارد کنید",
                "input_type": "NUMBER",
                "is_required": True,
                "validation_rules": {
                    "min_value": 100,
                    "max_value": 10000,
                },
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        question_id = question_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/questions/{question_id}/validate",
            json={
                "answer_text": "500",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_answer_choice_valid(self, client: AsyncClient, test_plan, admin_user):
        """Test validating a valid choice answer."""
        question_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "رنگ را انتخاب کنید",
                "input_type": "SINGLE_CHOICE",
                "is_required": True,
                "options": [
                    {"label_fa": "قرمز", "value": "red"},
                    {"label_fa": "آبی", "value": "blue"},
                ],
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        question_id = question_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/questions/{question_id}/validate",
            json={
                "answer_text": "red",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_answer_invalid_choice(self, client: AsyncClient, test_plan, admin_user):
        """Test validating an invalid choice answer."""
        question_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "رنگ را انتخاب کنید",
                "input_type": "SINGLE_CHOICE",
                "is_required": True,
                "options": [
                    {"label_fa": "قرمز", "value": "red"},
                    {"label_fa": "آبی", "value": "blue"},
                ],
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        question_id = question_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/questions/{question_id}/validate",
            json={
                "answer_text": "yellow",  # Not a valid option
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False

    # ==================== Error Cases ====================

    @pytest.mark.asyncio
    async def test_create_question_invalid_plan(self, client: AsyncClient, admin_user):
        """Test creating question for non-existent plan."""
        fake_plan_id = str(uuid4())
        
        response = await client.post(
            f"/api/v1/plans/{fake_plan_id}/questions",
            json={
                "question_fa": "سوال تست",
                "input_type": "TEXT",
                "is_required": True,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_question_invalid_input_type(self, client: AsyncClient, test_plan, admin_user):
        """Test creating question with invalid input type."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "سوال تست",
                "input_type": "INVALID_TYPE",
                "is_required": True,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_question_unauthorized(self, client: AsyncClient, test_plan):
        """Test that non-admin cannot create question."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/questions",
            json={
                "question_fa": "سوال غیرمجاز",
                "input_type": "TEXT",
                "is_required": True,
                "sort_order": 1,
            },
            # No admin header
        )
        
        assert response.status_code in [401, 403, 422]

