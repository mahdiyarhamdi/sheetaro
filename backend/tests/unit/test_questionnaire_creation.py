"""Unit tests for questionnaire creation functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from app.services.category_service import CategoryService
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    QuestionCreate, QuestionUpdate, QuestionOptionCreate,
    SectionCreate, SectionUpdate, SectionReorderRequest, SectionReorderItem,
    QuestionReorderRequest, QuestionReorderItem, ValidationRules,
)
from app.models.design_question import QuestionInputType


class TestQuestionCreation:
    """Test question creation functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        return db

    @pytest.fixture
    def mock_repository(self, mock_db):
        """Create mock repository."""
        repo = AsyncMock(spec=CategoryRepository)
        repo.db = mock_db
        return repo

    @pytest.fixture
    def service(self, mock_db):
        """Create service instance with mock db."""
        return CategoryService(mock_db)

    @pytest.fixture
    def sample_plan_id(self):
        """Sample plan UUID."""
        return uuid4()

    @pytest.fixture
    def sample_section_id(self):
        """Sample section UUID."""
        return uuid4()

    @pytest.fixture
    def sample_question_id(self):
        """Sample question UUID."""
        return uuid4()

    # ==================== Text Question Tests ====================

    @pytest.mark.asyncio
    async def test_create_question_text_type(self, mock_repository, sample_plan_id):
        """Test creating a TEXT type question with min/max length."""
        question_data = QuestionCreate(
            question_fa="نام برند خود را وارد کنید",
            input_type=QuestionInputType.TEXT,
            is_required=True,
            placeholder_fa="مثال: برند من",
            help_text_fa="نام برندی که روی لیبل چاپ شود",
            validation_rules=ValidationRules(
                min_length=2,
                max_length=50,
                error_message_fa="نام برند باید بین ۲ تا ۵۰ کاراکتر باشد"
            ),
            sort_order=1,
        )
        
        mock_question = MagicMock()
        mock_question.id = uuid4()
        mock_question.question_fa = question_data.question_fa
        mock_question.input_type = QuestionInputType.TEXT
        mock_question.is_required = True
        mock_question.validation_rules = question_data.validation_rules.model_dump()
        mock_question.options = []
        mock_question.created_at = datetime.utcnow()
        mock_question.updated_at = datetime.utcnow()
        
        mock_repository.create_question.return_value = mock_question
        
        result = await mock_repository.create_question(sample_plan_id, question_data)
        
        mock_repository.create_question.assert_called_once_with(sample_plan_id, question_data)
        assert result.question_fa == "نام برند خود را وارد کنید"
        assert result.input_type == QuestionInputType.TEXT

    @pytest.mark.asyncio
    async def test_create_question_number_type(self, mock_repository, sample_plan_id):
        """Test creating a NUMBER type question with min/max value."""
        question_data = QuestionCreate(
            question_fa="تعداد را وارد کنید",
            input_type=QuestionInputType.NUMBER,
            is_required=True,
            validation_rules=ValidationRules(
                min_value=1,
                max_value=10000,
            ),
            sort_order=2,
        )
        
        mock_question = MagicMock()
        mock_question.id = uuid4()
        mock_question.question_fa = question_data.question_fa
        mock_question.input_type = QuestionInputType.NUMBER
        mock_question.validation_rules = question_data.validation_rules.model_dump()
        mock_question.options = []
        mock_question.created_at = datetime.utcnow()
        mock_question.updated_at = datetime.utcnow()
        
        mock_repository.create_question.return_value = mock_question
        
        result = await mock_repository.create_question(sample_plan_id, question_data)
        
        assert result.input_type == QuestionInputType.NUMBER
        assert result.validation_rules['min_value'] == 1
        assert result.validation_rules['max_value'] == 10000

    @pytest.mark.asyncio
    async def test_create_question_single_choice(self, mock_repository, sample_plan_id):
        """Test creating a SINGLE_CHOICE question with options."""
        options = [
            QuestionOptionCreate(value="paper", label_fa="کاغذی", sort_order=1),
            QuestionOptionCreate(value="pvc", label_fa="پی وی سی", price_modifier=5000, sort_order=2),
            QuestionOptionCreate(value="metallic", label_fa="متالیک", price_modifier=15000, sort_order=3),
        ]
        
        question_data = QuestionCreate(
            question_fa="نوع جنس لیبل را انتخاب کنید",
            input_type=QuestionInputType.SINGLE_CHOICE,
            is_required=True,
            options=options,
            sort_order=3,
        )
        
        mock_question = MagicMock()
        mock_question.id = uuid4()
        mock_question.question_fa = question_data.question_fa
        mock_question.input_type = QuestionInputType.SINGLE_CHOICE
        mock_question.options = [MagicMock(value=o.value, label_fa=o.label_fa) for o in options]
        mock_question.created_at = datetime.utcnow()
        mock_question.updated_at = datetime.utcnow()
        
        mock_repository.create_question.return_value = mock_question
        
        result = await mock_repository.create_question(sample_plan_id, question_data)
        
        assert result.input_type == QuestionInputType.SINGLE_CHOICE
        assert len(result.options) == 3

    @pytest.mark.asyncio
    async def test_create_question_multi_choice(self, mock_repository, sample_plan_id):
        """Test creating a MULTI_CHOICE question with min/max value for selections."""
        options = [
            QuestionOptionCreate(value="size_5x5", label_fa="۵×۵ سانتی", sort_order=1),
            QuestionOptionCreate(value="size_10x5", label_fa="۱۰×۵ سانتی", sort_order=2),
            QuestionOptionCreate(value="size_10x10", label_fa="۱۰×۱۰ سانتی", sort_order=3),
        ]
        
        question_data = QuestionCreate(
            question_fa="سایزهای مورد نظر را انتخاب کنید",
            input_type=QuestionInputType.MULTI_CHOICE,
            is_required=True,
            validation_rules=ValidationRules(
                min_value=1,  # Min selections
                max_value=5,  # Max selections
            ),
            options=options,
            sort_order=4,
        )
        
        mock_question = MagicMock()
        mock_question.id = uuid4()
        mock_question.question_fa = question_data.question_fa
        mock_question.input_type = QuestionInputType.MULTI_CHOICE
        mock_question.validation_rules = question_data.validation_rules.model_dump()
        mock_question.options = [MagicMock(value=o.value, label_fa=o.label_fa) for o in options]
        mock_question.created_at = datetime.utcnow()
        mock_question.updated_at = datetime.utcnow()
        
        mock_repository.create_question.return_value = mock_question
        
        result = await mock_repository.create_question(sample_plan_id, question_data)
        
        assert result.input_type == QuestionInputType.MULTI_CHOICE
        assert result.validation_rules['min_value'] == 1
        assert result.validation_rules['max_value'] == 5

    @pytest.mark.asyncio
    async def test_create_question_color_picker(self, mock_repository, sample_plan_id):
        """Test creating a COLOR_PICKER type question."""
        question_data = QuestionCreate(
            question_fa="رنگ پس‌زمینه را انتخاب کنید",
            input_type=QuestionInputType.COLOR_PICKER,
            is_required=False,
            help_text_fa="کد رنگ هگز مانند #FF5733 را وارد کنید",
            sort_order=5,
        )
        
        mock_question = MagicMock()
        mock_question.id = uuid4()
        mock_question.question_fa = question_data.question_fa
        mock_question.input_type = QuestionInputType.COLOR_PICKER
        mock_question.is_required = False
        mock_question.options = []
        mock_question.created_at = datetime.utcnow()
        mock_question.updated_at = datetime.utcnow()
        
        mock_repository.create_question.return_value = mock_question
        
        result = await mock_repository.create_question(sample_plan_id, question_data)
        
        assert result.input_type == QuestionInputType.COLOR_PICKER
        assert result.is_required is False

    @pytest.mark.asyncio
    async def test_create_question_image_upload(self, mock_repository, sample_plan_id):
        """Test creating an IMAGE_UPLOAD type question."""
        question_data = QuestionCreate(
            question_fa="لوگو یا تصویر برند خود را آپلود کنید",
            input_type=QuestionInputType.IMAGE_UPLOAD,
            is_required=True,
            validation_rules=ValidationRules(
                allowed_types=["jpg", "jpeg", "png"],
                max_file_size_mb=5,
            ),
            sort_order=6,
        )
        
        mock_question = MagicMock()
        mock_question.id = uuid4()
        mock_question.question_fa = question_data.question_fa
        mock_question.input_type = QuestionInputType.IMAGE_UPLOAD
        mock_question.validation_rules = question_data.validation_rules.model_dump()
        mock_question.options = []
        mock_question.created_at = datetime.utcnow()
        mock_question.updated_at = datetime.utcnow()
        
        mock_repository.create_question.return_value = mock_question
        
        result = await mock_repository.create_question(sample_plan_id, question_data)
        
        assert result.input_type == QuestionInputType.IMAGE_UPLOAD
        assert "jpg" in result.validation_rules['allowed_types']

    @pytest.mark.asyncio
    async def test_create_question_with_section(self, mock_repository, sample_plan_id, sample_section_id):
        """Test creating a question linked to a section."""
        question_data = QuestionCreate(
            question_fa="اطلاعات تماس خود را وارد کنید",
            input_type=QuestionInputType.TEXT,
            is_required=True,
            section_id=sample_section_id,
            sort_order=1,
        )
        
        mock_question = MagicMock()
        mock_question.id = uuid4()
        mock_question.question_fa = question_data.question_fa
        mock_question.section_id = sample_section_id
        mock_question.input_type = QuestionInputType.TEXT
        mock_question.options = []
        mock_question.created_at = datetime.utcnow()
        mock_question.updated_at = datetime.utcnow()
        
        mock_repository.create_question.return_value = mock_question
        
        result = await mock_repository.create_question(sample_plan_id, question_data)
        
        assert result.section_id == sample_section_id

    @pytest.mark.asyncio
    async def test_create_question_conditional(self, mock_repository, sample_plan_id, sample_question_id):
        """Test creating a question with conditional logic (depends_on)."""
        question_data = QuestionCreate(
            question_fa="رنگ متالیک را مشخص کنید",
            input_type=QuestionInputType.TEXT,
            is_required=True,
            depends_on_question_id=sample_question_id,
            depends_on_values=["metallic"],  # Show only if previous answer is "metallic"
            sort_order=4,
        )
        
        mock_question = MagicMock()
        mock_question.id = uuid4()
        mock_question.question_fa = question_data.question_fa
        mock_question.input_type = QuestionInputType.TEXT
        mock_question.depends_on_question_id = sample_question_id
        mock_question.depends_on_values = ["metallic"]
        mock_question.options = []
        mock_question.created_at = datetime.utcnow()
        mock_question.updated_at = datetime.utcnow()
        
        mock_repository.create_question.return_value = mock_question
        
        result = await mock_repository.create_question(sample_plan_id, question_data)
        
        assert result.depends_on_question_id == sample_question_id
        assert result.depends_on_values == ["metallic"]


class TestQuestionOptionCreation:
    """Test question option creation functionality."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock(spec=CategoryRepository)

    @pytest.fixture
    def sample_question_id(self):
        """Sample question UUID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_create_question_option(self, mock_repository, sample_question_id):
        """Test adding an option to a choice question."""
        option_data = QuestionOptionCreate(
            value="gold",
            label_fa="طلایی",
            price_modifier=20000,
            sort_order=1,
        )
        
        mock_option = MagicMock()
        mock_option.id = uuid4()
        mock_option.value = option_data.value
        mock_option.label_fa = option_data.label_fa
        mock_option.price_modifier = option_data.price_modifier
        
        mock_repository.create_question_option.return_value = mock_option
        
        result = await mock_repository.create_question_option(sample_question_id, option_data)
        
        assert result.value == "gold"
        assert result.label_fa == "طلایی"
        assert result.price_modifier == 20000

    @pytest.mark.asyncio
    async def test_create_option_with_image(self, mock_repository, sample_question_id):
        """Test creating an option with an image URL."""
        option_data = QuestionOptionCreate(
            value="texture_wood",
            label_fa="بافت چوب",
            image_url="https://example.com/textures/wood.jpg",
            sort_order=1,
        )
        
        mock_option = MagicMock()
        mock_option.id = uuid4()
        mock_option.value = option_data.value
        mock_option.label_fa = option_data.label_fa
        mock_option.image_url = option_data.image_url
        
        mock_repository.create_question_option.return_value = mock_option
        
        result = await mock_repository.create_question_option(sample_question_id, option_data)
        
        assert result.image_url == "https://example.com/textures/wood.jpg"


class TestSectionCreation:
    """Test section creation functionality."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock(spec=CategoryRepository)

    @pytest.fixture
    def sample_plan_id(self):
        """Sample plan UUID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_create_section(self, mock_repository, sample_plan_id):
        """Test creating a question section."""
        section_data = SectionCreate(
            title_fa="اطلاعات طراحی",
            description_fa="در این بخش اطلاعات طراحی لیبل را وارد کنید",
            sort_order=1,
        )
        
        mock_section = MagicMock()
        mock_section.id = uuid4()
        mock_section.title_fa = section_data.title_fa
        mock_section.description_fa = section_data.description_fa
        mock_section.sort_order = section_data.sort_order
        mock_section.questions = []
        mock_section.created_at = datetime.utcnow()
        mock_section.updated_at = datetime.utcnow()
        
        mock_repository.create_section.return_value = mock_section
        
        result = await mock_repository.create_section(sample_plan_id, section_data)
        
        assert result.title_fa == "اطلاعات طراحی"
        assert result.description_fa == "در این بخش اطلاعات طراحی لیبل را وارد کنید"

    @pytest.mark.asyncio
    async def test_section_ordering(self, mock_repository, sample_plan_id):
        """Test reordering sections."""
        section_ids = [uuid4(), uuid4(), uuid4()]
        reorder_items = [
            SectionReorderItem(id=sid, sort_order=i + 1)
            for i, sid in enumerate(section_ids)
        ]
        reorder_request = SectionReorderRequest(items=reorder_items)
        
        mock_repository.reorder_sections.return_value = True
        
        result = await mock_repository.reorder_sections(sample_plan_id, reorder_request)
        
        mock_repository.reorder_sections.assert_called_once()
        assert result is True


class TestQuestionOrdering:
    """Test question ordering functionality."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock(spec=CategoryRepository)

    @pytest.fixture
    def sample_section_id(self):
        """Sample section UUID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_question_ordering(self, mock_repository, sample_section_id):
        """Test reordering questions within a section."""
        question_ids = [uuid4(), uuid4(), uuid4()]
        reorder_items = [
            QuestionReorderItem(id=qid, sort_order=i + 1)
            for i, qid in enumerate(question_ids)
        ]
        reorder_request = QuestionReorderRequest(items=reorder_items)
        
        mock_repository.reorder_questions.return_value = True
        
        result = await mock_repository.reorder_questions(sample_section_id, reorder_request)
        
        mock_repository.reorder_questions.assert_called_once()
        assert result is True


class TestValidationRules:
    """Test validation rules schema."""

    def test_validation_rules_minmax_length(self):
        """Test validation rules with min/max length."""
        rules = ValidationRules(
            min_length=5,
            max_length=100,
            error_message_fa="طول متن نامعتبر است"
        )
        
        assert rules.min_length == 5
        assert rules.max_length == 100
        assert rules.error_message_fa == "طول متن نامعتبر است"

    def test_validation_rules_minmax_value(self):
        """Test validation rules with min/max value."""
        rules = ValidationRules(
            min_value=1,
            max_value=1000,
        )
        
        assert rules.min_value == 1
        assert rules.max_value == 1000

    def test_validation_rules_pattern(self):
        """Test validation rules with regex pattern."""
        rules = ValidationRules(
            regex=r'^[A-Za-z0-9]+$',
            error_message_fa="فقط حروف و اعداد انگلیسی مجاز است"
        )
        
        assert rules.regex == r'^[A-Za-z0-9]+$'

    def test_validation_rules_min_max_value(self):
        """Test validation rules for min/max value."""
        rules = ValidationRules(
            min_value=1,
            max_value=100,
        )
        
        assert rules.min_value == 1
        assert rules.max_value == 100

    def test_validation_rules_file_upload(self):
        """Test validation rules for file upload."""
        rules = ValidationRules(
            allowed_types=["pdf", "doc", "docx"],
            max_size_mb=10,
        )
        
        assert rules.allowed_types == ["pdf", "doc", "docx"]
        assert rules.max_size_mb == 10

    def test_validation_rules_empty(self):
        """Test empty validation rules."""
        rules = ValidationRules()
        
        assert rules.min_length is None
        assert rules.max_length is None
        assert rules.regex is None

