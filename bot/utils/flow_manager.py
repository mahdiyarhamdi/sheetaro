"""Flow Manager - Unified state management for bot conversations.

This module provides a centralized way to manage conversation flow state,
replacing the problematic ConversationHandler approach.
"""

from typing import Optional, Any, Dict
from telegram.ext import ContextTypes


# Flow identifiers
FLOW_ADMIN = "admin"
FLOW_CATALOG = "catalog"
FLOW_ORDERS = "orders"
FLOW_PRODUCTS = "products"
FLOW_PROFILE = "profile"
FLOW_TRACKING = "tracking"
FLOW_QUESTIONNAIRE = "questionnaire"
FLOW_TEMPLATES = "templates"


def set_flow(
    context: ContextTypes.DEFAULT_TYPE,
    flow: str,
    step: str,
    data: Optional[Dict[str, Any]] = None
) -> None:
    """Set the current flow and step.
    
    Args:
        context: Telegram context
        flow: Flow identifier (e.g., 'catalog', 'admin')
        step: Current step within the flow (e.g., 'category_create_name')
        data: Optional flow-specific data to store
    """
    context.user_data['current_flow'] = flow
    context.user_data['flow_step'] = step
    if data is not None:
        context.user_data['flow_data'] = data


def get_flow(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Get the current flow identifier.
    
    Returns:
        Current flow name or None if no flow is active
    """
    return context.user_data.get('current_flow')


def get_step(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Get the current step within the flow.
    
    Returns:
        Current step name or None
    """
    return context.user_data.get('flow_step')


def get_flow_data(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    """Get the flow-specific data.
    
    Returns:
        Flow data dictionary (empty dict if none)
    """
    return context.user_data.get('flow_data', {})


def set_step(context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Update the current step without changing the flow.
    
    Args:
        context: Telegram context
        step: New step name
    """
    context.user_data['flow_step'] = step


def update_flow_data(context: ContextTypes.DEFAULT_TYPE, key: str, value: Any) -> None:
    """Update a specific key in flow data.
    
    Args:
        context: Telegram context
        key: Data key to update
        value: New value
    """
    if 'flow_data' not in context.user_data:
        context.user_data['flow_data'] = {}
    context.user_data['flow_data'][key] = value


def get_flow_data_item(context: ContextTypes.DEFAULT_TYPE, key: str, default: Any = None) -> Any:
    """Get a specific item from flow data.
    
    Args:
        context: Telegram context
        key: Data key to retrieve
        default: Default value if key not found
        
    Returns:
        The value or default
    """
    return context.user_data.get('flow_data', {}).get(key, default)


def clear_flow(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the current flow state.
    
    This should be called when exiting a flow (e.g., going back to main menu).
    """
    context.user_data.pop('current_flow', None)
    context.user_data.pop('flow_step', None)
    context.user_data.pop('flow_data', None)


def clear_flow_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear only the flow data, keeping flow and step."""
    context.user_data.pop('flow_data', None)


def is_in_flow(context: ContextTypes.DEFAULT_TYPE, flow: Optional[str] = None) -> bool:
    """Check if user is currently in a flow.
    
    Args:
        context: Telegram context
        flow: Optional specific flow to check. If None, checks if in any flow.
        
    Returns:
        True if in the specified flow (or any flow if flow is None)
    """
    current_flow = get_flow(context)
    if flow is None:
        return current_flow is not None
    return current_flow == flow


def is_at_step(context: ContextTypes.DEFAULT_TYPE, step: str) -> bool:
    """Check if user is at a specific step.
    
    Args:
        context: Telegram context
        step: Step name to check
        
    Returns:
        True if at the specified step
    """
    return get_step(context) == step


# Catalog flow steps
CATALOG_STEPS = {
    'menu': 'catalog_menu',
    'category_list': 'category_list',
    'category_actions': 'category_actions',
    'category_create_name': 'category_create_name',
    'category_create_slug': 'category_create_slug',
    'category_create_icon': 'category_create_icon',
    'category_create_price': 'category_create_price',
    'attribute_list': 'attribute_list',
    'attribute_actions': 'attribute_actions',
    'attribute_create_name': 'attribute_create_name',
    'attribute_create_slug': 'attribute_create_slug',
    'attribute_create_type': 'attribute_create_type',
    'option_list': 'option_list',
    'option_create_label': 'option_create_label',
    'option_create_value': 'option_create_value',
    'option_create_price': 'option_create_price',
    'plan_list': 'plan_list',
    'plan_actions': 'plan_actions',
    'plan_create_name': 'plan_create_name',
    'plan_create_slug': 'plan_create_slug',
    'plan_create_price': 'plan_create_price',
    'plan_create_type': 'plan_create_type',
    'question_list': 'question_list',
    'question_create_text': 'question_create_text',
    'question_create_type': 'question_create_type',
    'template_list': 'template_list',
    'template_create_name': 'template_create_name',
    'template_upload_preview': 'template_upload_preview',
    'template_set_placeholder': 'template_set_placeholder',
}

# Admin flow steps
ADMIN_STEPS = {
    'menu': 'admin_menu',
    'pending_list': 'pending_list',
    'payment_review': 'payment_review',
    'reject_reason': 'reject_reason',
    'admin_management': 'admin_management',
    'admin_info': 'admin_info',
    'add_admin_id': 'add_admin_id',
}

# Orders flow steps
ORDER_STEPS = {
    'menu': 'orders_menu',
    'list': 'orders_list',
    'details': 'order_details',
    'cancel_confirm': 'cancel_confirm',
    'payment': 'payment',
    'awaiting_receipt': 'awaiting_receipt',
}

# Products flow steps (legacy)
PRODUCT_STEPS = {
    'select_type': 'select_type',
    'select_product': 'select_product',
    'select_plan': 'select_plan',
    'select_quantity': 'select_quantity',
    'confirmation': 'confirmation',
    'payment': 'payment',
    'awaiting_receipt': 'awaiting_receipt',
}

# Profile flow steps
PROFILE_STEPS = {
    'view': 'profile_view',
    'edit_phone': 'edit_phone',
    'edit_city': 'edit_city',
    'edit_address': 'edit_address',
}

# Questionnaire flow steps
QUESTIONNAIRE_STEPS = {
    'start': 'questionnaire_start',
    'section_display': 'section_display',
    'question_display': 'question_display',
    'text_input': 'text_input',
    'number_input': 'number_input',
    'textarea_input': 'textarea_input',
    'color_picker': 'color_picker',
    'date_picker': 'date_picker',
    'scale_input': 'scale_input',
    'single_choice': 'single_choice',
    'multi_choice': 'multi_choice',
    'image_upload': 'image_upload',
    'file_upload': 'file_upload',
    'summary': 'questionnaire_summary',
}

# Template flow steps
TEMPLATE_STEPS = {
    'gallery': 'template_gallery',
    'preview': 'template_preview',
    'logo_upload': 'logo_upload',
    'design_preview': 'design_preview',
    'confirmation': 'design_confirmation',
}

