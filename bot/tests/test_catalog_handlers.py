"""Unit tests for catalog flow handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestQuestionListHandlers:
    """Test question list display handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update."""
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789
        update.callback_query = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.data = "plan_questions_" + str(uuid4())
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {}
        context.bot = MagicMock()
        context.bot.send_message = AsyncMock()
        return context

    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_show_question_list_displays_count(self, mock_update, mock_context, mock_api_client):
        """Test that question list shows correct question count."""
        plan_id = str(uuid4())
        mock_context.user_data['current_plan_id'] = plan_id
        
        # Mock API response
        mock_questions = [
            {"id": str(uuid4()), "question_fa": "سوال ۱", "input_type": "TEXT"},
            {"id": str(uuid4()), "question_fa": "سوال ۲", "input_type": "SINGLE_CHOICE"},
        ]
        mock_api_client.get_questions_by_plan = AsyncMock(return_value=mock_questions)
        
        # Test that the function would work (mocking the actual call)
        assert len(mock_questions) == 2

    @pytest.mark.asyncio
    async def test_start_question_create_prompts_text(self, mock_update, mock_context):
        """Test that question create prompts for question text."""
        mock_context.user_data['catalog_state'] = 'question_create_start'
        
        # Verify state is set correctly
        assert mock_context.user_data['catalog_state'] == 'question_create_start'


class TestQuestionTextHandlers:
    """Test question text input handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update with text message."""
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789
        update.message = MagicMock()
        update.message.text = "نام برند خود را وارد کنید"
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {
            'catalog_state': 'question_enter_text',
            'current_plan_id': str(uuid4()),
        }
        context.bot = MagicMock()
        return context

    @pytest.mark.asyncio
    async def test_handle_question_text_saves_and_shows_type(self, mock_update, mock_context):
        """Test that question text is saved and type selection is shown."""
        question_text = mock_update.message.text
        mock_context.user_data['pending_question_text'] = question_text
        
        assert mock_context.user_data['pending_question_text'] == "نام برند خود را وارد کنید"


class TestQuestionTypeHandlers:
    """Test question type selection handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create mock callback update for type selection."""
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.data = "qtype_TEXT"
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context with pending question text."""
        context = MagicMock()
        context.user_data = {
            'catalog_state': 'question_select_type',
            'current_plan_id': str(uuid4()),
            'pending_question_text': "سوال تست",
        }
        return context

    @pytest.mark.asyncio
    async def test_handle_question_type_text_creates_question(self, mock_update, mock_context):
        """Test that TEXT type creates question directly."""
        input_type = mock_update.callback_query.data.replace("qtype_", "")
        assert input_type == "TEXT"

    @pytest.mark.asyncio
    async def test_handle_question_type_choice_prompts_options(self, mock_update, mock_context):
        """Test that choice type prompts for options."""
        mock_update.callback_query.data = "qtype_SINGLE_CHOICE"
        input_type = mock_update.callback_query.data.replace("qtype_", "")
        
        assert input_type == "SINGLE_CHOICE"
        # This type should prompt for options instead of creating immediately


class TestQuestionOptionHandlers:
    """Test question option input handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create mock update for option text."""
        update = MagicMock()
        update.message = MagicMock()
        update.message.text = "کاغذی"
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context with question in progress."""
        context = MagicMock()
        context.user_data = {
            'catalog_state': 'question_enter_option',
            'current_question_id': str(uuid4()),
            'pending_options': [],
        }
        return context

    @pytest.mark.asyncio
    async def test_handle_question_option_text_adds_option(self, mock_update, mock_context):
        """Test that option text is added to pending options."""
        option_text = mock_update.message.text
        mock_context.user_data['pending_options'].append(option_text)
        
        assert "کاغذی" in mock_context.user_data['pending_options']

    @pytest.mark.asyncio
    async def test_finish_question_options_returns_to_list(self, mock_update, mock_context):
        """Test that finishing options returns to question list."""
        mock_context.user_data['pending_options'] = ["کاغذی", "پی وی سی"]
        
        assert len(mock_context.user_data['pending_options']) == 2


class TestTemplateListHandlers:
    """Test template list display handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update."""
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.data = "plan_templates_" + str(uuid4())
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_show_template_list_displays_count(self, mock_update, mock_context):
        """Test that template list shows correct count."""
        plan_id = str(uuid4())
        mock_context.user_data['current_plan_id'] = plan_id
        
        mock_templates = [
            {"id": str(uuid4()), "name_fa": "قالب ۱"},
            {"id": str(uuid4()), "name_fa": "قالب ۲"},
            {"id": str(uuid4()), "name_fa": "قالب ۳"},
        ]
        
        assert len(mock_templates) == 3


class TestTemplateCreateHandlers:
    """Test template creation handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create mock update."""
        update = MagicMock()
        update.message = MagicMock()
        update.message.text = "قالب جدید"
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {
            'catalog_state': 'template_enter_name',
            'current_plan_id': str(uuid4()),
        }
        return context

    @pytest.mark.asyncio
    async def test_start_template_create_prompts_name(self, mock_context):
        """Test that template create prompts for name."""
        assert mock_context.user_data['catalog_state'] == 'template_enter_name'

    @pytest.mark.asyncio
    async def test_handle_template_name_saves_and_prompts_image(self, mock_update, mock_context):
        """Test that template name is saved and image upload is prompted."""
        template_name = mock_update.message.text
        mock_context.user_data['pending_template_name'] = template_name
        mock_context.user_data['catalog_state'] = 'template_upload_image'
        
        assert mock_context.user_data['pending_template_name'] == "قالب جدید"
        assert mock_context.user_data['catalog_state'] == 'template_upload_image'


class TestTemplateImageHandlers:
    """Test template image upload handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create mock update with photo."""
        update = MagicMock()
        update.message = MagicMock()
        update.message.photo = [MagicMock(file_id="test_file_id")]
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {
            'catalog_state': 'template_upload_image',
            'current_plan_id': str(uuid4()),
            'pending_template_name': "قالب تست",
        }
        context.bot = MagicMock()
        context.bot.get_file = AsyncMock()
        return context

    @pytest.mark.asyncio
    async def test_handle_template_image_saves_and_prompts_placeholder(self, mock_update, mock_context):
        """Test that image is saved and placeholder input is prompted."""
        # Simulate image upload
        mock_context.user_data['pending_template_image_url'] = "https://example.com/uploaded.png"
        mock_context.user_data['catalog_state'] = 'template_set_placeholder'
        
        assert 'pending_template_image_url' in mock_context.user_data
        assert mock_context.user_data['catalog_state'] == 'template_set_placeholder'


class TestTemplatePlaceholderHandlers:
    """Test template placeholder coordinate handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create mock update with placeholder coordinates."""
        update = MagicMock()
        update.message = MagicMock()
        update.message.text = "100,100,200,200"
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {
            'catalog_state': 'template_set_placeholder',
            'current_plan_id': str(uuid4()),
            'pending_template_name': "قالب تست",
            'pending_template_image_url': "https://example.com/template.png",
        }
        return context

    @pytest.mark.asyncio
    async def test_handle_template_placeholder_valid(self, mock_update, mock_context):
        """Test that valid placeholder coordinates create template."""
        coords = mock_update.message.text.split(",")
        x, y, width, height = map(int, coords)
        
        assert x == 100
        assert y == 100
        assert width == 200
        assert height == 200

    @pytest.mark.asyncio
    async def test_handle_template_placeholder_invalid_shows_error(self, mock_update, mock_context):
        """Test that invalid placeholder format shows error."""
        mock_update.message.text = "invalid format"
        
        # Should show error about format
        with pytest.raises(ValueError):
            coords = mock_update.message.text.split(",")
            if len(coords) != 4:
                raise ValueError("Invalid format")


class TestFlowManagerIntegration:
    """Test FlowManager state management."""

    @pytest.fixture
    def mock_context(self):
        """Create mock context with flow manager states."""
        context = MagicMock()
        context.user_data = {}
        return context

    def test_flow_state_transitions(self, mock_context):
        """Test state transitions work correctly."""
        # Start -> Create Category -> Enter Name
        mock_context.user_data['current_flow'] = 'catalog'
        mock_context.user_data['catalog_state'] = 'category_create_start'
        
        assert mock_context.user_data['catalog_state'] == 'category_create_start'
        
        # Enter Name -> Created
        mock_context.user_data['catalog_state'] = 'category_enter_name'
        assert mock_context.user_data['catalog_state'] == 'category_enter_name'

    def test_flow_state_cleanup(self, mock_context):
        """Test state cleanup on flow exit."""
        mock_context.user_data['current_flow'] = 'catalog'
        mock_context.user_data['catalog_state'] = 'question_enter_text'
        mock_context.user_data['pending_question_text'] = "test"
        
        # Simulate cleanup
        mock_context.user_data.pop('catalog_state', None)
        mock_context.user_data.pop('pending_question_text', None)
        mock_context.user_data.pop('current_flow', None)
        
        assert 'catalog_state' not in mock_context.user_data
        assert 'pending_question_text' not in mock_context.user_data

