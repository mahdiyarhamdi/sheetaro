"""Unit tests for QuestionnaireService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.questionnaire_service import QuestionnaireService
from app.schemas.category import ValidateAnswerRequest, ValidationRules
from app.models.design_question import DesignQuestion, QuestionOption, QuestionInputType
from app.repositories.category_repository import CategoryRepository


class TestQuestionnaireService:
    """Test QuestionnaireService methods."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock(spec=CategoryRepository)

    @pytest.fixture
    def service(self, mock_repository):
        """Create service instance."""
        return QuestionnaireService(mock_repository)

    @pytest.fixture
    def text_question(self):
        """Create a TEXT type question."""
        question = MagicMock(spec=DesignQuestion)
        question.id = uuid4()
        question.question_fa = "نام برند خود را وارد کنید"
        question.input_type = QuestionInputType.TEXT
        question.is_required = True
        question.validation_rules = {"min_length": 2, "max_length": 50}
        question.options = []
        return question

    @pytest.fixture
    def number_question(self):
        """Create a NUMBER type question."""
        question = MagicMock(spec=DesignQuestion)
        question.id = uuid4()
        question.question_fa = "تعداد را وارد کنید"
        question.input_type = QuestionInputType.NUMBER
        question.is_required = True
        question.validation_rules = {"min_value": 1, "max_value": 1000}
        question.options = []
        return question

    @pytest.fixture
    def single_choice_question(self):
        """Create a SINGLE_CHOICE type question."""
        question = MagicMock(spec=DesignQuestion)
        question.id = uuid4()
        question.question_fa = "رنگ را انتخاب کنید"
        question.input_type = QuestionInputType.SINGLE_CHOICE
        question.is_required = True
        question.validation_rules = None
        
        opt1 = MagicMock(spec=QuestionOption)
        opt1.value = "red"
        opt1.label_fa = "قرمز"
        opt1.is_active = True
        
        opt2 = MagicMock(spec=QuestionOption)
        opt2.value = "blue"
        opt2.label_fa = "آبی"
        opt2.is_active = True
        
        opt3 = MagicMock(spec=QuestionOption)
        opt3.value = "green"
        opt3.label_fa = "سبز"
        opt3.is_active = True
        
        question.options = [opt1, opt2, opt3]
        return question

    @pytest.fixture
    def multi_choice_question(self):
        """Create a MULTI_CHOICE type question."""
        question = MagicMock(spec=DesignQuestion)
        question.id = uuid4()
        question.question_fa = "سایزها را انتخاب کنید"
        question.input_type = QuestionInputType.MULTI_CHOICE
        question.is_required = True
        question.validation_rules = None
        
        opt1 = MagicMock(spec=QuestionOption)
        opt1.value = "small"
        opt1.label_fa = "کوچک"
        opt1.is_active = True
        
        opt2 = MagicMock(spec=QuestionOption)
        opt2.value = "medium"
        opt2.label_fa = "متوسط"
        opt2.is_active = True
        
        opt3 = MagicMock(spec=QuestionOption)
        opt3.value = "large"
        opt3.label_fa = "بزرگ"
        opt3.is_active = True
        
        question.options = [opt1, opt2, opt3]
        return question

    @pytest.fixture
    def color_picker_question(self):
        """Create a COLOR_PICKER type question."""
        question = MagicMock(spec=DesignQuestion)
        question.id = uuid4()
        question.question_fa = "رنگ را انتخاب کنید"
        question.input_type = QuestionInputType.COLOR_PICKER
        question.is_required = True
        question.validation_rules = None
        question.options = []
        return question

    # ==================== Text Validation Tests ====================

    def test_validate_text_answer_valid(self, service, text_question):
        """Test valid text answer."""
        request = ValidateAnswerRequest(answer_text="نام برند تست")
        result = service.validate_answer(text_question, request)
        
        assert result.is_valid is True

    def test_validate_text_answer_too_short(self, service, text_question):
        """Test text answer that's too short."""
        request = ValidateAnswerRequest(answer_text="آ")
        result = service.validate_answer(text_question, request)
        
        assert result.is_valid is False
        assert result.error_message is not None

    def test_validate_text_answer_too_long(self, service, text_question):
        """Test text answer that's too long."""
        request = ValidateAnswerRequest(answer_text="آ" * 100)
        result = service.validate_answer(text_question, request)
        
        assert result.is_valid is False
        assert result.error_message is not None

    def test_validate_required_text_empty(self, service, text_question):
        """Test empty answer for required question."""
        request = ValidateAnswerRequest(answer_text="")
        result = service.validate_answer(text_question, request)
        
        assert result.is_valid is False
        assert "اجباری" in result.error_message

    # ==================== Number Validation Tests ====================

    def test_validate_number_answer_valid(self, service, number_question):
        """Test valid number answer."""
        request = ValidateAnswerRequest(answer_text="500")
        result = service.validate_answer(number_question, request)
        
        assert result.is_valid is True

    def test_validate_number_answer_below_min(self, service, number_question):
        """Test number below minimum."""
        request = ValidateAnswerRequest(answer_text="0")
        result = service.validate_answer(number_question, request)
        
        assert result.is_valid is False

    def test_validate_number_answer_above_max(self, service, number_question):
        """Test number above maximum."""
        request = ValidateAnswerRequest(answer_text="5000")
        result = service.validate_answer(number_question, request)
        
        assert result.is_valid is False

    def test_validate_number_answer_not_number(self, service, number_question):
        """Test non-numeric input for number question."""
        request = ValidateAnswerRequest(answer_text="abc")
        result = service.validate_answer(number_question, request)
        
        assert result.is_valid is False

    # ==================== Single Choice Validation Tests ====================

    def test_validate_single_choice_valid(self, service, single_choice_question):
        """Test valid single choice answer."""
        request = ValidateAnswerRequest(answer_text="red")
        result = service.validate_answer(single_choice_question, request)
        
        assert result.is_valid is True

    def test_validate_single_choice_invalid_option(self, service, single_choice_question):
        """Test invalid option for single choice."""
        request = ValidateAnswerRequest(answer_text="yellow")
        result = service.validate_answer(single_choice_question, request)
        
        assert result.is_valid is False

    # ==================== Multi Choice Validation Tests ====================

    def test_validate_multi_choice_valid(self, service, multi_choice_question):
        """Test valid multi choice answer."""
        request = ValidateAnswerRequest(answer_values=["small", "medium"])
        result = service.validate_answer(multi_choice_question, request)
        
        assert result.is_valid is True

    def test_validate_multi_choice_empty_required(self, service, multi_choice_question):
        """Test multi choice with no selections when required."""
        request = ValidateAnswerRequest(answer_values=[])
        result = service.validate_answer(multi_choice_question, request)
        
        assert result.is_valid is False

    def test_validate_multi_choice_invalid_option(self, service, multi_choice_question):
        """Test multi choice with invalid option."""
        request = ValidateAnswerRequest(answer_values=["small", "extra_large"])
        result = service.validate_answer(multi_choice_question, request)
        
        assert result.is_valid is False

    # ==================== Color Picker Validation Tests ====================

    def test_validate_color_valid_hex(self, service, color_picker_question):
        """Test valid hex color."""
        request = ValidateAnswerRequest(answer_text="#FF5733")
        result = service.validate_answer(color_picker_question, request)
        
        assert result.is_valid is True

    def test_validate_color_valid_short_hex(self, service, color_picker_question):
        """Test valid short hex color."""
        request = ValidateAnswerRequest(answer_text="#F00")
        result = service.validate_answer(color_picker_question, request)
        
        assert result.is_valid is True

    def test_validate_color_invalid_hex(self, service, color_picker_question):
        """Test invalid hex color."""
        request = ValidateAnswerRequest(answer_text="not-a-color")
        result = service.validate_answer(color_picker_question, request)
        
        assert result.is_valid is False

    # ==================== Optional Question Tests ====================

    def test_validate_optional_empty(self, service, text_question):
        """Test empty answer for optional question."""
        text_question.is_required = False
        request = ValidateAnswerRequest(answer_text="")
        result = service.validate_answer(text_question, request)
        
        assert result.is_valid is True

    # ==================== Regex Pattern Validation ====================

    def test_validate_regex_pattern_valid(self, service, text_question):
        """Test answer matching regex pattern."""
        text_question.validation_rules = {"regex": r"^[\w\.-]+@[\w\.-]+\.\w+$"}
        request = ValidateAnswerRequest(answer_text="test@example.com")
        result = service.validate_answer(text_question, request)
        
        assert result.is_valid is True

    def test_validate_regex_pattern_invalid(self, service, text_question):
        """Test answer not matching regex pattern."""
        text_question.validation_rules = {"regex": r"^[\w\.-]+@[\w\.-]+\.\w+$"}
        request = ValidateAnswerRequest(answer_text="not-an-email")
        result = service.validate_answer(text_question, request)
        
        assert result.is_valid is False

    # ==================== Conditional Logic Tests ====================

    def test_should_show_question_no_depends(self, service, text_question):
        """Test question with no dependencies always shows."""
        text_question.depends_on_question_id = None
        
        result = service.should_show_question(text_question, {})
        
        assert result is True

    def test_should_show_question_depends_match(self, service, text_question):
        """Test question shows when dependency matches."""
        dep_question_id = uuid4()
        text_question.depends_on_question_id = dep_question_id
        text_question.depends_on_values = ["option_a"]
        
        answers = {dep_question_id: "option_a"}
        result = service.should_show_question(text_question, answers)
        
        assert result is True

    def test_should_show_question_depends_no_match(self, service, text_question):
        """Test question hides when dependency doesn't match."""
        dep_question_id = uuid4()
        text_question.depends_on_question_id = dep_question_id
        text_question.depends_on_values = ["option_a"]
        
        answers = {dep_question_id: "option_b"}
        result = service.should_show_question(text_question, answers)
        
        assert result is False

    def test_should_show_question_depends_no_answer(self, service, text_question):
        """Test question hides when dependency has no answer."""
        dep_question_id = uuid4()
        text_question.depends_on_question_id = dep_question_id
        text_question.depends_on_values = ["option_a"]
        
        answers = {}
        result = service.should_show_question(text_question, answers)
        
        assert result is False

    # ==================== Filter Visible Questions Tests ====================

    def test_filter_visible_questions(self, service, text_question, number_question):
        """Test filtering visible questions."""
        text_question.depends_on_question_id = None
        number_question.depends_on_question_id = text_question.id
        number_question.depends_on_values = ["specific_answer"]
        
        questions = [text_question, number_question]
        answers = {text_question.id: "other_answer"}
        
        visible = service.filter_visible_questions(questions, answers)
        
        # Only text_question should be visible
        assert len(visible) == 1
        assert visible[0] == text_question
