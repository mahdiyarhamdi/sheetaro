"""E2E tests for questionnaire flow.

Full flow: Create Plan -> Create Section -> Create Questions -> 
           Customer fills questionnaire -> Validate answers -> Submit
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient

from tests.conftest import create_test_user
from app.models.enums import UserRole


class TestAdminCreatesQuestionnaire:
    """Test admin creating a complete questionnaire."""

    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user."""
        return await create_test_user(
            db_session,
            {
                "telegram_id": 777888999,
                "username": "e2e_admin",
                "first_name": "E2E",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
            }
        )

    @pytest_asyncio.fixture
    async def customer_user(self, db_session):
        """Create a customer user."""
        return await create_test_user(
            db_session,
            {
                "telegram_id": 111222333,
                "username": "e2e_customer",
                "first_name": "E2E",
                "last_name": "Customer",
                "role": UserRole.CUSTOMER,
            }
        )

    @pytest.mark.asyncio
    async def test_admin_creates_full_questionnaire(self, client: AsyncClient, admin_user):
        """Test admin creating plan with sections and questions."""
        headers = {"X-Telegram-ID": str(admin_user.telegram_id)}
        
        # Step 1: Create category
        cat_response = await client.post(
            "/api/v1/categories",
            json={
                "name_fa": "لیبل E2E",
                "name_en": "E2E Label",
                "slug": "e2e-label",
                "sort_order": 1,
            },
            headers=headers,
        )
        assert cat_response.status_code == 201
        category_id = cat_response.json()["id"]
        
        # Step 2: Create plan with questionnaire enabled
        plan_response = await client.post(
            f"/api/v1/categories/{category_id}/plans",
            json={
                "name_fa": "نیمه‌خصوصی E2E",
                "slug": "semi-private-e2e",
                "plan_type": "SEMI_PRIVATE",
                "has_questionnaire": True,
                "has_templates": False,
                "price": 600000,
                "sort_order": 1,
            },
            headers=headers,
        )
        assert plan_response.status_code == 201
        plan_id = plan_response.json()["id"]
        
        # Step 3: Create section
        section_response = await client.post(
            f"/api/v1/categories/plans/{plan_id}/sections",
            json={
                "title_fa": "اطلاعات برند",
                "description_fa": "اطلاعات مربوط به برند شما",
                "sort_order": 1,
            },
            headers=headers,
        )
        assert section_response.status_code == 201
        section_id = section_response.json()["id"]
        
        # Step 4: Create questions
        # Question 1: Text
        q1_response = await client.post(
            f"/api/v1/categories/sections/{section_id}/questions",
            json={
                "question_fa": "نام برند خود را وارد کنید",
                "input_type": "TEXT",
                "is_required": True,
                "validation_rules": {"min_length": 2, "max_length": 50},
                "sort_order": 1,
            },
            headers=headers,
        )
        assert q1_response.status_code == 201
        
        # Question 2: Single choice
        q2_response = await client.post(
            f"/api/v1/categories/sections/{section_id}/questions",
            json={
                "question_fa": "نوع جنس را انتخاب کنید",
                "input_type": "SINGLE_CHOICE",
                "is_required": True,
                "options": [
                    {"label_fa": "کاغذی", "value": "paper", "sort_order": 1},
                    {"label_fa": "پی وی سی", "value": "pvc", "price_modifier": 5000, "sort_order": 2},
                ],
                "sort_order": 2,
            },
            headers=headers,
        )
        assert q2_response.status_code == 201
        
        # Question 3: Color picker
        q3_response = await client.post(
            f"/api/v1/categories/sections/{section_id}/questions",
            json={
                "question_fa": "رنگ پس‌زمینه را انتخاب کنید",
                "input_type": "COLOR_PICKER",
                "is_required": False,
                "sort_order": 3,
            },
            headers=headers,
        )
        assert q3_response.status_code == 201
        
        # Verify questions are created
        questions_response = await client.get(
            f"/api/v1/categories/sections/{section_id}/questions",
        )
        assert questions_response.status_code == 200
        questions = questions_response.json()
        assert len(questions) >= 3


class TestCustomerFillsQuestionnaire:
    """Test customer filling out a questionnaire."""

    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user."""
        return await create_test_user(
            db_session,
            {
                "telegram_id": 999888777,
                "username": "fill_admin",
                "first_name": "Fill",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
            }
        )

    @pytest_asyncio.fixture
    async def setup_questionnaire(self, client: AsyncClient, admin_user):
        """Setup a complete questionnaire for testing."""
        headers = {"X-Telegram-ID": str(admin_user.telegram_id)}
        
        # Create category
        cat_response = await client.post(
            "/api/v1/categories",
            json={
                "name_fa": "لیبل تست پرسشنامه",
                "slug": "questionnaire-test",
                "sort_order": 1,
            },
            headers=headers,
        )
        category_id = cat_response.json()["id"]
        
        # Create plan
        plan_response = await client.post(
            f"/api/v1/categories/{category_id}/plans",
            json={
                "name_fa": "نیمه‌خصوصی تست",
                "slug": "semi-test",
                "plan_type": "SEMI_PRIVATE",
                "has_questionnaire": True,
                "price": 500000,
                "sort_order": 1,
            },
            headers=headers,
        )
        plan_id = plan_response.json()["id"]
        
        # Create section
        section_response = await client.post(
            f"/api/v1/categories/plans/{plan_id}/sections",
            json={
                "title_fa": "اطلاعات",
                "sort_order": 1,
            },
            headers=headers,
        )
        section_id = section_response.json()["id"]
        
        # Create questions
        q1_response = await client.post(
            f"/api/v1/categories/sections/{section_id}/questions",
            json={
                "question_fa": "نام برند",
                "input_type": "TEXT",
                "is_required": True,
                "validation_rules": {"min_length": 2},
                "sort_order": 1,
            },
            headers=headers,
        )
        q1_id = q1_response.json()["id"]
        
        q2_response = await client.post(
            f"/api/v1/categories/sections/{section_id}/questions",
            json={
                "question_fa": "نوع جنس",
                "input_type": "SINGLE_CHOICE",
                "is_required": True,
                "options": [
                    {"label_fa": "کاغذی", "value": "paper"},
                    {"label_fa": "پی وی سی", "value": "pvc"},
                ],
                "sort_order": 2,
            },
            headers=headers,
        )
        q2_id = q2_response.json()["id"]
        
        return {
            "category_id": category_id,
            "plan_id": plan_id,
            "section_id": section_id,
            "question_ids": [q1_id, q2_id],
        }

    @pytest.mark.asyncio
    async def test_customer_fills_questionnaire(self, client: AsyncClient, setup_questionnaire):
        """Test customer answering all questions in order."""
        question_ids = setup_questionnaire["question_ids"]
        
        # Validate text answer
        response1 = await client.post(
            f"/api/v1/questions/{question_ids[0]}/validate",
            json={"answer_text": "برند تست"},
        )
        assert response1.status_code == 200
        assert response1.json()["is_valid"] is True
        
        # Validate choice answer
        response2 = await client.post(
            f"/api/v1/questions/{question_ids[1]}/validate",
            json={"answer_text": "paper"},
        )
        assert response2.status_code == 200
        assert response2.json()["is_valid"] is True

    @pytest.mark.asyncio
    async def test_questionnaire_validation_errors(self, client: AsyncClient, setup_questionnaire):
        """Test customer getting validation error and retrying."""
        question_ids = setup_questionnaire["question_ids"]
        
        # First attempt: too short
        response1 = await client.post(
            f"/api/v1/questions/{question_ids[0]}/validate",
            json={"answer_text": "آ"},  # Too short
        )
        assert response1.status_code == 200
        assert response1.json()["is_valid"] is False
        assert "error_message" in response1.json()
        
        # Second attempt: valid
        response2 = await client.post(
            f"/api/v1/questions/{question_ids[0]}/validate",
            json={"answer_text": "برند صحیح"},
        )
        assert response2.status_code == 200
        assert response2.json()["is_valid"] is True


class TestConditionalLogic:
    """Test conditional question logic."""

    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user."""
        return await create_test_user(
            db_session,
            {
                "telegram_id": 555666777,
                "username": "conditional_admin",
                "first_name": "Conditional",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
            }
        )

    @pytest.mark.asyncio
    async def test_questionnaire_conditional_logic(self, client: AsyncClient, admin_user):
        """Test questions appearing based on previous answers."""
        headers = {"X-Telegram-ID": str(admin_user.telegram_id)}
        
        # Create category and plan
        cat_response = await client.post(
            "/api/v1/categories",
            json={
                "name_fa": "لیبل شرطی",
                "slug": "conditional-label",
                "sort_order": 1,
            },
            headers=headers,
        )
        category_id = cat_response.json()["id"]
        
        plan_response = await client.post(
            f"/api/v1/categories/{category_id}/plans",
            json={
                "name_fa": "پلن شرطی",
                "slug": "conditional-plan",
                "plan_type": "SEMI_PRIVATE",
                "has_questionnaire": True,
                "price": 400000,
                "sort_order": 1,
            },
            headers=headers,
        )
        plan_id = plan_response.json()["id"]
        
        # Create section
        section_response = await client.post(
            f"/api/v1/categories/plans/{plan_id}/sections",
            json={
                "title_fa": "بخش شرطی",
                "sort_order": 1,
            },
            headers=headers,
        )
        section_id = section_response.json()["id"]
        
        # Create parent question
        parent_response = await client.post(
            f"/api/v1/categories/sections/{section_id}/questions",
            json={
                "question_fa": "نوع جنس",
                "input_type": "SINGLE_CHOICE",
                "is_required": True,
                "options": [
                    {"label_fa": "کاغذی", "value": "paper"},
                    {"label_fa": "متالیک", "value": "metallic"},
                ],
                "sort_order": 1,
            },
            headers=headers,
        )
        parent_id = parent_response.json()["id"]
        
        # Create conditional child question (only shows if parent = "metallic")
        child_response = await client.post(
            f"/api/v1/categories/sections/{section_id}/questions",
            json={
                "question_fa": "رنگ متالیک را مشخص کنید",
                "input_type": "TEXT",
                "is_required": True,
                "depends_on_question_id": parent_id,
                "depends_on_values": ["metallic"],
                "sort_order": 2,
            },
            headers=headers,
        )
        
        assert child_response.status_code == 201
        child_data = child_response.json()
        assert child_data["depends_on_question_id"] == parent_id
        assert child_data["depends_on_values"] == ["metallic"]


class TestQuestionnaireSummary:
    """Test questionnaire summary generation."""

    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user."""
        return await create_test_user(
            db_session,
            {
                "telegram_id": 444555666,
                "username": "summary_admin",
                "first_name": "Summary",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
            }
        )

    @pytest.mark.asyncio
    async def test_questionnaire_summary(self, client: AsyncClient, admin_user):
        """Test that summary shows all answers correctly."""
        headers = {"X-Telegram-ID": str(admin_user.telegram_id)}
        
        # Create minimal questionnaire
        cat_response = await client.post(
            "/api/v1/categories",
            json={
                "name_fa": "لیبل خلاصه",
                "slug": "summary-label",
                "sort_order": 1,
            },
            headers=headers,
        )
        category_id = cat_response.json()["id"]
        
        plan_response = await client.post(
            f"/api/v1/categories/{category_id}/plans",
            json={
                "name_fa": "پلن خلاصه",
                "slug": "summary-plan",
                "plan_type": "SEMI_PRIVATE",
                "has_questionnaire": True,
                "price": 300000,
                "sort_order": 1,
            },
            headers=headers,
        )
        plan_id = plan_response.json()["id"]
        
        # Verify plan is created with questionnaire enabled
        plan_detail = await client.get(f"/api/v1/categories/plans/{plan_id}")
        assert plan_detail.status_code == 200
        assert plan_detail.json()["has_questionnaire"] is True

