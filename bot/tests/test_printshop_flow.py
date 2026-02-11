"""Tests for Print Shop flow handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


# ==================== Show Print Shop Menu Tests ====================


class TestShowPrintShopMenu:
    """Tests for show_printshop_menu handler."""

    @pytest.mark.asyncio
    async def test_show_menu_replies_with_text(
        self, mock_telegram_update, mock_context
    ):
        """PSBOT-01: Show menu displays print shop panel message."""
        from handlers.flows.printshop_flow import show_printshop_menu

        await show_printshop_menu(mock_telegram_update, mock_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args
        assert "پنل چاپخانه" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_show_menu_sets_flow(
        self, mock_telegram_update, mock_context
    ):
        """PSBOT-02: Show menu sets the correct flow and step."""
        from handlers.flows.printshop_flow import show_printshop_menu

        await show_printshop_menu(mock_telegram_update, mock_context)

        assert mock_context.user_data.get('current_flow') == 'print_shop'
        assert mock_context.user_data.get('flow_step') == 'printshop_menu'


# ==================== Menu Text Handling Tests ====================


class TestHandlePrintShopMenuText:
    """Tests for handle_printshop_menu_text handler."""

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.show_order_queue", new_callable=AsyncMock)
    async def test_queue_selection_calls_show_queue(
        self, mock_show_queue, mock_telegram_update, mock_context
    ):
        """PSBOT-03: Selecting 'صف سفارش' calls show_order_queue."""
        from handlers.flows.printshop_flow import handle_printshop_menu_text

        mock_telegram_update.message.text = "📋 صف سفارش‌ها"
        await handle_printshop_menu_text(mock_telegram_update, mock_context)

        mock_show_queue.assert_called_once()

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.show_my_orders_menu", new_callable=AsyncMock)
    async def test_my_orders_selection(
        self, mock_show_my_orders, mock_telegram_update, mock_context
    ):
        """PSBOT-04: Selecting 'سفارش‌های من' calls show_my_orders_menu."""
        from handlers.flows.printshop_flow import handle_printshop_menu_text

        mock_telegram_update.message.text = "📦 سفارش‌های من"
        await handle_printshop_menu_text(mock_telegram_update, mock_context)

        mock_show_my_orders.assert_called_once()

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.show_stats", new_callable=AsyncMock)
    async def test_stats_selection(
        self, mock_show_stats, mock_telegram_update, mock_context
    ):
        """PSBOT-05: Selecting 'آمار' calls show_stats."""
        from handlers.flows.printshop_flow import handle_printshop_menu_text

        mock_telegram_update.message.text = "📊 آمار"
        await handle_printshop_menu_text(mock_telegram_update, mock_context)

        mock_show_stats.assert_called_once()

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.show_settlements", new_callable=AsyncMock)
    async def test_settlements_selection(
        self, mock_show_settlements, mock_telegram_update, mock_context
    ):
        """PSBOT-06: Selecting 'تسویه' calls show_settlements."""
        from handlers.flows.printshop_flow import handle_printshop_menu_text

        mock_telegram_update.message.text = "💰 تسویه‌حساب"
        await handle_printshop_menu_text(mock_telegram_update, mock_context)

        mock_show_settlements.assert_called_once()

    @pytest.mark.asyncio
    async def test_back_clears_flow(
        self, mock_telegram_update, mock_context
    ):
        """PSBOT-07: Selecting 'بازگشت' clears the flow."""
        from handlers.flows.printshop_flow import handle_printshop_menu_text

        mock_telegram_update.message.text = "🔙 بازگشت"
        mock_context.user_data['current_flow'] = 'print_shop'
        mock_context.user_data['flow_step'] = 'printshop_menu'

        await handle_printshop_menu_text(mock_telegram_update, mock_context)

        assert mock_context.user_data.get('current_flow') is None

    @pytest.mark.asyncio
    async def test_unknown_option_shows_error(
        self, mock_telegram_update, mock_context
    ):
        """PSBOT-08: Unknown text shows invalid option message."""
        from handlers.flows.printshop_flow import handle_printshop_menu_text

        mock_telegram_update.message.text = "something random"
        await handle_printshop_menu_text(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "نامعتبر" in call_args[0][0]


# ==================== Order Queue Tests ====================


class TestShowOrderQueue:
    """Tests for show_order_queue handler."""

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_show_queue_with_orders(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-09: Queue shows orders when available."""
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.get_printshop_queue = AsyncMock(return_value={
            "items": [
                {
                    "id": str(uuid4()),
                    "quantity": 100,
                    "total_price": "50000",
                    "customer_name": "Customer",
                    "customer_city": "Tehran",
                    "created_at": "2026-01-04T10:00:00Z",
                }
            ],
            "total": 1,
        })

        await _import_show_queue()(mock_telegram_update, mock_context)

        mock_telegram_update.message.reply_text.assert_called()
        call_args = mock_telegram_update.message.reply_text.call_args
        assert "آماده چاپ" in call_args[0][0]

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_show_queue_empty(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-10: Queue shows empty message when no orders."""
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.get_printshop_queue = AsyncMock(return_value={"items": [], "total": 0})

        await _import_show_queue()(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "خالی" in call_args[0][0]

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_show_queue_user_not_found(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-11: Queue shows error when user not found."""
        mock_api.get_user = AsyncMock(return_value=None)

        await _import_show_queue()(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "خطا" in call_args[0][0]


# ==================== Stats Tests ====================


class TestShowStats:
    """Tests for show_stats handler."""

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_show_stats_success(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-12: Stats displayed correctly."""
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.get_printshop_stats = AsyncMock(return_value={
            "total_orders": 50,
            "pending_orders": 5,
            "in_progress_orders": 3,
            "printed_orders": 10,
            "shipped_orders": 20,
            "delivered_orders": 12,
            "avg_print_time_hours": 4.5,
            "avg_ship_time_hours": 12.0,
            "sla_compliance_percent": 95.0,
        })

        await _import_show_stats()(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "آمار" in call_args[0][0]

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_show_stats_error(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-13: Stats shows error on API failure."""
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.get_printshop_stats = AsyncMock(return_value=None)

        await _import_show_stats()(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "خطا" in call_args[0][0]


# ==================== Settlements Tests ====================


class TestShowSettlements:
    """Tests for show_settlements handler."""

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_show_settlements_with_data(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-14: Settlements displayed when data exists."""
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.get_printshop_settlements = AsyncMock(return_value={
            "items": [
                {
                    "id": str(uuid4()),
                    "period_start": "2026-01-01",
                    "period_end": "2026-01-31",
                    "total_orders": 10,
                    "net_amount": "900000",
                    "status": "PENDING",
                }
            ],
            "total": 1,
        })

        await _import_show_settlements()(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "تسویه" in call_args[0][0]

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_show_settlements_empty(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-15: Shows empty message when no settlements."""
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.get_printshop_settlements = AsyncMock(return_value={"items": [], "total": 0})

        await _import_show_settlements()(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "ثبت نشده" in call_args[0][0]


# ==================== Tracking Code Input Tests ====================


class TestHandleTrackingCodeInput:
    """Tests for handle_tracking_code_input handler."""

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_tracking_code_too_short(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-16: Rejects tracking code shorter than 5 chars."""
        from handlers.flows.printshop_flow import handle_tracking_code_input

        mock_telegram_update.message.text = "1234"
        mock_context.user_data['flow_data'] = {"shipping_order_id": str(uuid4())}

        await handle_tracking_code_input(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "حداقل" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_tracking_code_no_order_selected(
        self, mock_telegram_update, mock_context
    ):
        """PSBOT-17: Shows error when no order is selected."""
        from handlers.flows.printshop_flow import handle_tracking_code_input

        mock_telegram_update.message.text = "POST-12345"
        mock_context.user_data['flow_data'] = {}

        await handle_tracking_code_input(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "خطا" in call_args[0][0]

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_tracking_code_success(
        self, mock_api, mock_telegram_update, mock_context
    ):
        """PSBOT-18: Successful tracking code submission."""
        from handlers.flows.printshop_flow import handle_tracking_code_input

        order_id = str(uuid4())
        mock_telegram_update.message.text = "POST-12345"
        mock_context.user_data['flow_data'] = {"shipping_order_id": order_id}
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.printshop_ship_order = AsyncMock(return_value={"status": "SHIPPED"})

        await handle_tracking_code_input(mock_telegram_update, mock_context)

        call_args = mock_telegram_update.message.reply_text.call_args
        assert "ارسال شد" in call_args[0][0]


# ==================== Callback Handler Tests ====================


class TestHandlePrintshopCallback:
    """Tests for handle_printshop_callback handler."""

    @pytest.mark.asyncio
    async def test_non_ps_prefix_returns_false(
        self, mock_telegram_update_with_callback, mock_context
    ):
        """PSBOT-19: Non-ps_ prefixed callbacks are ignored."""
        from handlers.flows.printshop_flow import handle_printshop_callback

        mock_telegram_update_with_callback.callback_query.data = "other_action"
        result = await handle_printshop_callback(
            mock_telegram_update_with_callback, mock_context
        )
        assert result is False

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_back_menu_callback(
        self, mock_api, mock_telegram_update_with_callback, mock_context
    ):
        """PSBOT-20: ps_back_menu callback returns to menu."""
        from handlers.flows.printshop_flow import handle_printshop_callback

        mock_telegram_update_with_callback.callback_query.data = "ps_back_menu"
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})

        result = await handle_printshop_callback(
            mock_telegram_update_with_callback, mock_context
        )

        assert result is True
        assert mock_context.user_data.get('flow_step') == 'printshop_menu'

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_accept_order_callback(
        self, mock_api, mock_telegram_update_with_callback, mock_context
    ):
        """PSBOT-21: ps_accept_ callback accepts order."""
        from handlers.flows.printshop_flow import handle_printshop_callback

        order_id = str(uuid4())
        mock_telegram_update_with_callback.callback_query.data = f"ps_accept_{order_id}"
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.printshop_accept_order = AsyncMock(return_value={"status": "PRINTING"})

        result = await handle_printshop_callback(
            mock_telegram_update_with_callback, mock_context
        )

        assert result is True
        mock_api.printshop_accept_order.assert_called_once()

    @pytest.mark.asyncio
    @patch("handlers.flows.printshop_flow.api_client")
    async def test_complete_printing_callback(
        self, mock_api, mock_telegram_update_with_callback, mock_context
    ):
        """PSBOT-22: ps_complete_ callback completes printing."""
        from handlers.flows.printshop_flow import handle_printshop_callback

        order_id = str(uuid4())
        mock_telegram_update_with_callback.callback_query.data = f"ps_complete_{order_id}"
        mock_api.get_user = AsyncMock(return_value={"id": str(uuid4())})
        mock_api.printshop_complete_order = AsyncMock(return_value={"status": "PRINTED"})

        result = await handle_printshop_callback(
            mock_telegram_update_with_callback, mock_context
        )

        assert result is True
        mock_api.printshop_complete_order.assert_called_once()


# ==================== Helper Imports ====================


def _import_show_queue():
    """Import show_order_queue to avoid import issues with mocking."""
    from handlers.flows.printshop_flow import show_order_queue
    return show_order_queue


def _import_show_stats():
    """Import show_stats."""
    from handlers.flows.printshop_flow import show_stats
    return show_stats


def _import_show_settlements():
    """Import show_settlements."""
    from handlers.flows.printshop_flow import show_settlements
    return show_settlements
