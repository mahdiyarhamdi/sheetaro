"""Unit tests for QuestionnaireService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.questionnaire_service import QuestionnaireService


class TestQuestionnaireService:
    """Test QuestionnaireService methods."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        """Create service instance."""
        return QuestionnaireService(mock_db)

    @pytest.fixture
    def sample_question(self):
        """Sample question data."""
        return {
            'id': 'q-123',
            'text_fa': 'نام برند خود را وارد کنید',
            'input_type': 'TEXT',
            'is_required': True,
            'validation_rules': {
                'min_length': 2,
                'max_length': 50
            }
        }

    @pytest.fixture
    def sample_number_question(self):
        """Sample number question data."""
        return {
            'id': 'q-456',
            'text_fa': 'تعداد را وارد کنید',
            'input_type': 'NUMBER',
            'is_required': True,
            'validation_rules': {
                'min_value': 1,
                'max_value': 1000
            }
        }

    @pytest.fixture
    def sample_single_choice_question(self):
        """Sample single choice question data."""
        return {
            'id': 'q-789',
            'text_fa': 'رنگ را انتخاب کنید',
            'input_type': 'SINGLE_CHOICE',
            'is_required': True,
            'options': [
                {'id': 'opt-1', 'value': 'red', 'label_fa': 'قرمز'},
                {'id': 'opt-2', 'value': 'blue', 'label_fa': 'آبی'},
                {'id': 'opt-3', 'value': 'green', 'label_fa': 'سبز'},
            ]
        }

    @pytest.fixture
    def sample_multi_choice_question(self):
        """Sample multi choice question data."""
        return {
            'id': 'q-multi',
            'text_fa': 'سایزها را انتخاب کنید',
            'input_type': 'MULTI_CHOICE',
            'is_required': True,
            'validation_rules': {
                'min_selections': 1,
                'max_selections': 3
            },
            'options': [
                {'id': 'opt-s', 'value': 'small', 'label_fa': 'کوچک'},
                {'id': 'opt-m', 'value': 'medium', 'label_fa': 'متوسط'},
                {'id': 'opt-l', 'value': 'large', 'label_fa': 'بزرگ'},
            ]
        }

    # ==================== Text Validation Tests ====================

    @pytest.mark.asyncio
    async def test_validate_text_answer_valid(self, service, sample_question):
        """Test valid text answer."""
        with patch.object(service, 'get_question', return_value=sample_question):
            result = await service.validate_answer(
                'q-123',
                {'answer_text': 'نام برند تست'}
            )
            assert result['is_valid'] is True

    @pytest.mark.asyncio
    async def test_validate_text_answer_too_short(self, service, sample_question):
        """Test text answer that's too short."""
        with patch.object(service, 'get_question', return_value=sample_question):
            result = await service.validate_answer(
                'q-123',
                {'answer_text': 'آ'}
            )
            assert result['is_valid'] is False
            assert 'حداقل' in result.get('error_message', '')

    @pytest.mark.asyncio
    async def test_validate_text_answer_too_long(self, service, sample_question):
        """Test text answer that's too long."""
        with patch.object(service, 'get_question', return_value=sample_question):
            result = await service.validate_answer(
                'q-123',
                {'answer_text': 'آ' * 100}
            )
            assert result['is_valid'] is False
            assert 'حداکثر' in result.get('error_message', '')

    @pytest.mark.asyncio
    async def test_validate_required_text_empty(self, service, sample_question):
        """Test empty answer for required question."""
        with patch.object(service, 'get_question', return_value=sample_question):
            result = await service.validate_answer(
                'q-123',
                {'answer_text': ''}
            )
            assert result['is_valid'] is False
            assert 'اجباری' in result.get('error_message', '')

    # ==================== Number Validation Tests ====================

    @pytest.mark.asyncio
    async def test_validate_number_answer_valid(self, service, sample_number_question):
        """Test valid number answer."""
        with patch.object(service, 'get_question', return_value=sample_number_question):
            result = await service.validate_answer(
                'q-456',
                {'answer_text': '500'}
            )
            assert result['is_valid'] is True

    @pytest.mark.asyncio
    async def test_validate_number_answer_below_min(self, service, sample_number_question):
        """Test number below minimum."""
        with patch.object(service, 'get_question', return_value=sample_number_question):
            result = await service.validate_answer(
                'q-456',
                {'answer_text': '0'}
            )
            assert result['is_valid'] is False

    @pytest.mark.asyncio
    async def test_validate_number_answer_above_max(self, service, sample_number_question):
        """Test number above maximum."""
        with patch.object(service, 'get_question', return_value=sample_number_question):
            result = await service.validate_answer(
                'q-456',
                {'answer_text': '5000'}
            )
            assert result['is_valid'] is False

    @pytest.mark.asyncio
    async def test_validate_number_answer_not_number(self, service, sample_number_question):
        """Test non-numeric input for number question."""
        with patch.object(service, 'get_question', return_value=sample_number_question):
            result = await service.validate_answer(
                'q-456',
                {'answer_text': 'abc'}
            )
            assert result['is_valid'] is False

    # ==================== Single Choice Validation Tests ====================

    @pytest.mark.asyncio
    async def test_validate_single_choice_valid(self, service, sample_single_choice_question):
        """Test valid single choice answer."""
        with patch.object(service, 'get_question', return_value=sample_single_choice_question):
            result = await service.validate_answer(
                'q-789',
                {'answer_text': 'red'}
            )
            assert result['is_valid'] is True

    @pytest.mark.asyncio
    async def test_validate_single_choice_invalid_option(self, service, sample_single_choice_question):
        """Test invalid option for single choice."""
        with patch.object(service, 'get_question', return_value=sample_single_choice_question):
            result = await service.validate_answer(
                'q-789',
                {'answer_text': 'yellow'}
            )
            assert result['is_valid'] is False

    # ==================== Multi Choice Validation Tests ====================

    @pytest.mark.asyncio
    async def test_validate_multi_choice_valid(self, service, sample_multi_choice_question):
        """Test valid multi choice answer."""
        with patch.object(service, 'get_question', return_value=sample_multi_choice_question):
            result = await service.validate_answer(
                'q-multi',
                {'answer_values': ['small', 'medium']}
            )
            assert result['is_valid'] is True

    @pytest.mark.asyncio
    async def test_validate_multi_choice_too_few(self, service, sample_multi_choice_question):
        """Test multi choice with too few selections."""
        with patch.object(service, 'get_question', return_value=sample_multi_choice_question):
            result = await service.validate_answer(
                'q-multi',
                {'answer_values': []}
            )
            assert result['is_valid'] is False

    @pytest.mark.asyncio
    async def test_validate_multi_choice_too_many(self, service, sample_multi_choice_question):
        """Test multi choice with too many selections."""
        sample_multi_choice_question['validation_rules']['max_selections'] = 2
        with patch.object(service, 'get_question', return_value=sample_multi_choice_question):
            result = await service.validate_answer(
                'q-multi',
                {'answer_values': ['small', 'medium', 'large']}
            )
            assert result['is_valid'] is False

    @pytest.mark.asyncio
    async def test_validate_multi_choice_invalid_option(self, service, sample_multi_choice_question):
        """Test multi choice with invalid option."""
        with patch.object(service, 'get_question', return_value=sample_multi_choice_question):
            result = await service.validate_answer(
                'q-multi',
                {'answer_values': ['small', 'extra_large']}
            )
            assert result['is_valid'] is False

    # ==================== Color Picker Validation Tests ====================

    @pytest.mark.asyncio
    async def test_validate_color_valid_hex(self, service):
        """Test valid hex color."""
        color_question = {
            'id': 'q-color',
            'text_fa': 'رنگ را انتخاب کنید',
            'input_type': 'COLOR_PICKER',
            'is_required': True,
        }
        with patch.object(service, 'get_question', return_value=color_question):
            result = await service.validate_answer(
                'q-color',
                {'answer_text': '#FF5733'}
            )
            assert result['is_valid'] is True

    @pytest.mark.asyncio
    async def test_validate_color_invalid_hex(self, service):
        """Test invalid hex color."""
        color_question = {
            'id': 'q-color',
            'text_fa': 'رنگ را انتخاب کنید',
            'input_type': 'COLOR_PICKER',
            'is_required': True,
        }
        with patch.object(service, 'get_question', return_value=color_question):
            result = await service.validate_answer(
                'q-color',
                {'answer_text': 'not-a-color'}
            )
            assert result['is_valid'] is False

    # ==================== Date Validation Tests ====================

    @pytest.mark.asyncio
    async def test_validate_date_valid(self, service):
        """Test valid date."""
        date_question = {
            'id': 'q-date',
            'text_fa': 'تاریخ را انتخاب کنید',
            'input_type': 'DATE_PICKER',
            'is_required': True,
        }
        with patch.object(service, 'get_question', return_value=date_question):
            result = await service.validate_answer(
                'q-date',
                {'answer_text': '1403/01/15'}
            )
            assert result['is_valid'] is True

    # ==================== Scale Validation Tests ====================

    @pytest.mark.asyncio
    async def test_validate_scale_valid(self, service):
        """Test valid scale answer."""
        scale_question = {
            'id': 'q-scale',
            'text_fa': 'امتیاز دهید',
            'input_type': 'SCALE',
            'is_required': True,
            'validation_rules': {
                'min_value': 1,
                'max_value': 5
            }
        }
        with patch.object(service, 'get_question', return_value=scale_question):
            result = await service.validate_answer(
                'q-scale',
                {'answer_text': '4'}
            )
            assert result['is_valid'] is True

    @pytest.mark.asyncio
    async def test_validate_scale_out_of_range(self, service):
        """Test scale answer out of range."""
        scale_question = {
            'id': 'q-scale',
            'text_fa': 'امتیاز دهید',
            'input_type': 'SCALE',
            'is_required': True,
            'validation_rules': {
                'min_value': 1,
                'max_value': 5
            }
        }
        with patch.object(service, 'get_question', return_value=scale_question):
            result = await service.validate_answer(
                'q-scale',
                {'answer_text': '10'}
            )
            assert result['is_valid'] is False

    # ==================== Optional Question Tests ====================

    @pytest.mark.asyncio
    async def test_validate_optional_empty(self, service, sample_question):
        """Test empty answer for optional question."""
        sample_question['is_required'] = False
        with patch.object(service, 'get_question', return_value=sample_question):
            result = await service.validate_answer(
                'q-123',
                {'answer_text': ''}
            )
            assert result['is_valid'] is True

    # ==================== Regex Pattern Validation ====================

    @pytest.mark.asyncio
    async def test_validate_regex_pattern_valid(self, service):
        """Test answer matching regex pattern."""
        email_question = {
            'id': 'q-email',
            'text_fa': 'ایمیل خود را وارد کنید',
            'input_type': 'TEXT',
            'is_required': True,
            'validation_rules': {
                'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'
            }
        }
        with patch.object(service, 'get_question', return_value=email_question):
            result = await service.validate_answer(
                'q-email',
                {'answer_text': 'test@example.com'}
            )
            assert result['is_valid'] is True

    @pytest.mark.asyncio
    async def test_validate_regex_pattern_invalid(self, service):
        """Test answer not matching regex pattern."""
        email_question = {
            'id': 'q-email',
            'text_fa': 'ایمیل خود را وارد کنید',
            'input_type': 'TEXT',
            'is_required': True,
            'validation_rules': {
                'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'
            }
        }
        with patch.object(service, 'get_question', return_value=email_question):
            result = await service.validate_answer(
                'q-email',
                {'answer_text': 'not-an-email'}
            )
            assert result['is_valid'] is False

