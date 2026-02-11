"""Tests for Print Shop keyboard generators."""

import pytest
from uuid import uuid4
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup


class TestPrintShopMenuKeyboard:
    """Tests for get_printshop_menu_keyboard."""

    def test_returns_reply_keyboard(self):
        """PSKB-01: Menu keyboard is a ReplyKeyboardMarkup."""
        from keyboards.printshop import get_printshop_menu_keyboard
        kb = get_printshop_menu_keyboard()
        assert isinstance(kb, ReplyKeyboardMarkup)

    def test_contains_queue_button(self):
        """PSKB-02: Menu contains queue button."""
        from keyboards.printshop import get_printshop_menu_keyboard
        kb = get_printshop_menu_keyboard()
        all_text = [btn.text if hasattr(btn, 'text') else str(btn) for row in kb.keyboard for btn in row]
        assert any("صف" in text for text in all_text)

    def test_contains_my_orders_button(self):
        """PSKB-03: Menu contains my orders button."""
        from keyboards.printshop import get_printshop_menu_keyboard
        kb = get_printshop_menu_keyboard()
        all_text = [btn.text if hasattr(btn, 'text') else str(btn) for row in kb.keyboard for btn in row]
        assert any("سفارش" in text for text in all_text)

    def test_contains_back_button(self):
        """PSKB-04: Menu contains back button."""
        from keyboards.printshop import get_printshop_menu_keyboard
        kb = get_printshop_menu_keyboard()
        all_text = [btn.text if hasattr(btn, 'text') else str(btn) for row in kb.keyboard for btn in row]
        assert any("بازگشت" in text for text in all_text)


class TestOrderQueueKeyboard:
    """Tests for get_order_queue_keyboard."""

    def test_returns_inline_keyboard(self):
        """PSKB-05: Queue keyboard is an InlineKeyboardMarkup."""
        from keyboards.printshop import get_order_queue_keyboard
        kb = get_order_queue_keyboard([])
        assert isinstance(kb, InlineKeyboardMarkup)

    def test_empty_orders_has_refresh_and_back(self):
        """PSKB-06: Empty queue still has refresh and back buttons."""
        from keyboards.printshop import get_order_queue_keyboard
        kb = get_order_queue_keyboard([])
        flat = [btn for row in kb.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in flat]
        assert "ps_refresh_queue" in callback_data
        assert "ps_back_menu" in callback_data

    def test_orders_create_buttons(self):
        """PSKB-07: Each order gets its own button."""
        from keyboards.printshop import get_order_queue_keyboard
        order_id = str(uuid4())
        orders = [{"id": order_id, "quantity": 100, "customer_city": "Tehran"}]
        kb = get_order_queue_keyboard(orders)
        flat = [btn for row in kb.inline_keyboard for btn in row]
        assert any(f"ps_queue_{order_id}" == btn.callback_data for btn in flat)


class TestQueueOrderDetailKeyboard:
    """Tests for get_queue_order_detail_keyboard."""

    def test_contains_accept_button(self):
        """PSKB-08: Detail keyboard has accept button."""
        from keyboards.printshop import get_queue_order_detail_keyboard
        order_id = str(uuid4())
        kb = get_queue_order_detail_keyboard(order_id)
        flat = [btn for row in kb.inline_keyboard for btn in row]
        assert any(f"ps_accept_{order_id}" == btn.callback_data for btn in flat)


class TestMyOrdersFilterKeyboard:
    """Tests for get_my_orders_filter_keyboard."""

    def test_contains_status_filters(self):
        """PSKB-09: Filter keyboard has status filter buttons."""
        from keyboards.printshop import get_my_orders_filter_keyboard
        kb = get_my_orders_filter_keyboard()
        flat = [btn for row in kb.inline_keyboard for btn in row]
        callback_data = [btn.callback_data for btn in flat]
        assert "ps_myorders_all" in callback_data
        assert "ps_myorders_PRINTING" in callback_data
        assert "ps_myorders_PRINTED" in callback_data


class TestMyOrderActionsKeyboard:
    """Tests for get_my_order_actions_keyboard."""

    def test_printing_order_has_complete_button(self):
        """PSKB-10: PRINTING order shows complete button."""
        from keyboards.printshop import get_my_order_actions_keyboard
        order_id = str(uuid4())
        order = {"id": order_id, "status": "PRINTING"}
        kb = get_my_order_actions_keyboard(order)
        flat = [btn for row in kb.inline_keyboard for btn in row]
        assert any(f"ps_complete_{order_id}" == btn.callback_data for btn in flat)

    def test_printed_order_has_ship_button(self):
        """PSKB-11: PRINTED order shows ship button."""
        from keyboards.printshop import get_my_order_actions_keyboard
        order_id = str(uuid4())
        order = {"id": order_id, "status": "PRINTED"}
        kb = get_my_order_actions_keyboard(order)
        flat = [btn for row in kb.inline_keyboard for btn in row]
        assert any(f"ps_ship_{order_id}" == btn.callback_data for btn in flat)

    def test_shipped_order_has_no_action_buttons(self):
        """PSKB-12: SHIPPED order has no action buttons (only back)."""
        from keyboards.printshop import get_my_order_actions_keyboard
        order_id = str(uuid4())
        order = {"id": order_id, "status": "SHIPPED"}
        kb = get_my_order_actions_keyboard(order)
        flat = [btn for row in kb.inline_keyboard for btn in row]
        # Should only have back button
        action_buttons = [
            btn for btn in flat
            if not btn.callback_data.startswith("ps_myorders_")
        ]
        assert len(action_buttons) == 0


class TestTrackingConfirmKeyboard:
    """Tests for get_tracking_confirm_keyboard."""

    def test_contains_cancel_button(self):
        """PSKB-13: Tracking keyboard has cancel button."""
        from keyboards.printshop import get_tracking_confirm_keyboard
        order_id = str(uuid4())
        kb = get_tracking_confirm_keyboard(order_id)
        flat = [btn for row in kb.inline_keyboard for btn in row]
        assert any(f"ps_myorder_{order_id}" == btn.callback_data for btn in flat)
