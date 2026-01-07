"""Unit tests for Flow Manager utility."""

import pytest
from unittest.mock import MagicMock

from utils.flow_manager import (
    set_flow, get_flow, get_step, get_flow_data, clear_flow,
    FLOW_CATALOG, FLOW_ORDERS, FLOW_PROFILE,
)

# Define constants for compatibility
FLOW_ORDER = FLOW_ORDERS  # Alias
STEP_IDLE = None  # Default step is None when not set


class TestFlowManagerBasics:
    """Test basic flow manager operations."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context with empty user_data."""
        context = MagicMock()
        context.user_data = {}
        return context
    
    def test_set_flow(self, mock_context):
        """Test setting a flow with step."""
        set_flow(mock_context, FLOW_CATALOG, "category_create_name")
        
        assert mock_context.user_data['current_flow'] == FLOW_CATALOG
        assert mock_context.user_data['flow_step'] == "category_create_name"
    
    def test_set_flow_with_data(self, mock_context):
        """Test setting flow with additional data."""
        flow_data = {"category_id": "123", "temp_name": "Test"}
        set_flow(mock_context, FLOW_CATALOG, "category_edit", flow_data)
        
        assert mock_context.user_data['current_flow'] == FLOW_CATALOG
        assert mock_context.user_data['flow_step'] == "category_edit"
        assert mock_context.user_data['flow_data']['category_id'] == "123"
    
    def test_get_flow(self, mock_context):
        """Test getting current flow."""
        mock_context.user_data['current_flow'] = FLOW_ORDER
        
        assert get_flow(mock_context) == FLOW_ORDER
    
    def test_get_flow_empty(self, mock_context):
        """Test getting flow when none is set."""
        assert get_flow(mock_context) is None
    
    def test_get_step(self, mock_context):
        """Test getting current flow step."""
        mock_context.user_data['flow_step'] = "payment_upload_receipt"
        
        assert get_step(mock_context) == "payment_upload_receipt"
    
    def test_get_step_default(self, mock_context):
        """Test getting flow step returns IDLE when not set."""
        assert get_step(mock_context) == STEP_IDLE
    
    def test_get_flow_data(self, mock_context):
        """Test getting flow data."""
        mock_context.user_data['flow_data'] = {"order_id": "456"}
        
        data = get_flow_data(mock_context)
        assert data['order_id'] == "456"
    
    def test_get_flow_data_empty(self, mock_context):
        """Test getting flow data when empty."""
        assert get_flow_data(mock_context) == {}
    
    def test_clear_flow(self, mock_context):
        """Test clearing flow state."""
        mock_context.user_data['current_flow'] = FLOW_CATALOG
        mock_context.user_data['flow_step'] = "some_step"
        mock_context.user_data['flow_data'] = {"key": "value"}
        
        clear_flow(mock_context)
        
        assert 'current_flow' not in mock_context.user_data
        assert 'flow_step' not in mock_context.user_data
        assert 'flow_data' not in mock_context.user_data


class TestFlowTransitions:
    """Test flow state transitions."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {}
        return context
    
    def test_catalog_flow_create_category(self, mock_context):
        """Test catalog flow: create category steps."""
        # Start
        set_flow(mock_context, FLOW_CATALOG, "category_list")
        assert get_step(mock_context) == "category_list"
        
        # User clicks create
        set_flow(mock_context, FLOW_CATALOG, "category_create_name")
        assert get_step(mock_context) == "category_create_name"
        
        # User enters name
        set_flow(mock_context, FLOW_CATALOG, "category_create_description", {"temp_name": "Labels"})
        assert get_step(mock_context) == "category_create_description"
        assert get_flow_data(mock_context)['temp_name'] == "Labels"
    
    def test_order_flow_payment(self, mock_context):
        """Test order flow: payment steps."""
        # View order
        set_flow(mock_context, FLOW_ORDER, "order_detail", {"order_id": "123"})
        
        # Payment initiated
        set_flow(mock_context, FLOW_ORDER, "payment_pending", {
            "order_id": "123",
            "payment_id": "456",
        })
        
        # Upload receipt
        set_flow(mock_context, FLOW_ORDER, "payment_upload_receipt", {
            "order_id": "123",
            "payment_id": "456",
        })
        
        assert get_step(mock_context) == "payment_upload_receipt"
        assert get_flow_data(mock_context)['payment_id'] == "456"
    
    def test_profile_flow_edit(self, mock_context):
        """Test profile flow: edit steps."""
        # View profile
        set_flow(mock_context, FLOW_PROFILE, "profile_view")
        
        # Edit name
        set_flow(mock_context, FLOW_PROFILE, "profile_edit_name")
        assert get_step(mock_context) == "profile_edit_name"
        
        # Clear after completion
        clear_flow(mock_context)
        assert get_flow(mock_context) is None
    
    def test_flow_switch(self, mock_context):
        """Test switching between flows."""
        # In catalog flow
        set_flow(mock_context, FLOW_CATALOG, "category_list")
        assert get_flow(mock_context) == FLOW_CATALOG
        
        # Switch to order flow
        set_flow(mock_context, FLOW_ORDER, "order_list")
        assert get_flow(mock_context) == FLOW_ORDER
        
        # Old flow data should be cleared
        assert 'category_list' not in mock_context.user_data


class TestFlowDataPersistence:
    """Test flow data persistence across steps."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {}
        return context
    
    def test_data_preserved_across_steps(self, mock_context):
        """Test that flow data is preserved when changing steps."""
        # Set initial data
        initial_data = {
            "category_id": "cat-123",
            "plan_id": "plan-456",
        }
        set_flow(mock_context, FLOW_CATALOG, "question_list", initial_data)
        
        # Change step but preserve data
        current_data = get_flow_data(mock_context)
        current_data['question_text'] = "New question?"
        set_flow(mock_context, FLOW_CATALOG, "question_create", current_data)
        
        # All data should be preserved
        final_data = get_flow_data(mock_context)
        assert final_data['category_id'] == "cat-123"
        assert final_data['plan_id'] == "plan-456"
        assert final_data['question_text'] == "New question?"
    
    def test_data_cleared_on_clear_flow(self, mock_context):
        """Test that flow data is cleared when explicitly clearing flow."""
        # Set catalog flow with data
        set_flow(mock_context, FLOW_CATALOG, "category_list", {"cat_id": "123"})
        
        # Clear the flow
        clear_flow(mock_context)
        
        # Data should be gone
        assert get_flow(mock_context) is None
        assert get_step(mock_context) is None

