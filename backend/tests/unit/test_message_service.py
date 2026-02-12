"""Tests for MessageService."""

import pytest
import pytest_asyncio
from decimal import Decimal

from app.models.enums import DesignPlan, OrderStatus, UserRole
from app.services.message_service import MessageService

from tests.conftest import (
    create_test_user,
    create_test_category,
    create_test_order,
)


@pytest_asyncio.fixture
async def customer(db_session):
    return await create_test_user(db_session, {
        "telegram_id": 333333,
        "username": "msg_customer",
        "first_name": "Msg",
        "last_name": "Customer",
        "role": UserRole.CUSTOMER,
        "phone_number": "09123330000",
    })


@pytest_asyncio.fixture
async def designer(db_session):
    return await create_test_user(db_session, {
        "telegram_id": 444444,
        "username": "msg_designer",
        "first_name": "Msg",
        "last_name": "Designer",
        "role": UserRole.DESIGNER,
        "phone_number": "09124440000",
    })


@pytest_asyncio.fixture
async def outsider(db_session):
    return await create_test_user(db_session, {
        "telegram_id": 555555,
        "username": "outsider",
        "first_name": "Out",
        "last_name": "Sider",
        "role": UserRole.CUSTOMER,
        "phone_number": "09125550000",
    })


@pytest_asyncio.fixture
async def category(db_session):
    return await create_test_category(db_session, {
        "slug": "msg-test-cat",
        "name_fa": "دسته تست پیام",
        "base_price": 10000,
        "is_active": True,
    })


@pytest_asyncio.fixture
async def private_order(db_session, customer, designer, category):
    """A PRIVATE order in DESIGNING status."""
    return await create_test_order(db_session, customer, category, {
        "design_plan": DesignPlan.PRIVATE,
        "status": OrderStatus.DESIGNING,
        "assigned_designer_id": designer.id,
        "revision_count": 0,
        "max_revisions": None,
        "validation_requested": False,
    })


@pytest_asyncio.fixture
async def semi_private_order(db_session, customer, designer, category):
    """A SEMI_PRIVATE order in DESIGNING status."""
    return await create_test_order(db_session, customer, category, {
        "design_plan": DesignPlan.SEMI_PRIVATE,
        "status": OrderStatus.DESIGNING,
        "assigned_designer_id": designer.id,
        "revision_count": 0,
        "max_revisions": 3,
        "validation_requested": False,
    })


@pytest.mark.asyncio
async def test_send_message_private(db_session, private_order, customer):
    """Customer can send message on PRIVATE order."""
    service = MessageService(db_session)
    msg = await service.send_message(
        order_id=private_order.id,
        sender_id=customer.id,
        content="Hello designer!",
    )

    assert msg.content == "Hello designer!"
    assert msg.sender_id == customer.id
    assert msg.order_id == private_order.id
    assert msg.is_read is False


@pytest.mark.asyncio
async def test_designer_can_send_message(db_session, private_order, designer):
    """Designer can send message on PRIVATE order."""
    service = MessageService(db_session)
    msg = await service.send_message(
        order_id=private_order.id,
        sender_id=designer.id,
        content="Hi customer!",
    )
    assert msg.content == "Hi customer!"
    assert msg.sender_id == designer.id


@pytest.mark.asyncio
async def test_send_message_semi_private_forbidden(db_session, semi_private_order, customer):
    """Chat is forbidden on SEMI_PRIVATE orders."""
    service = MessageService(db_session)
    with pytest.raises(PermissionError, match="PRIVATE"):
        await service.send_message(
            order_id=semi_private_order.id,
            sender_id=customer.id,
            content="Should fail",
        )


@pytest.mark.asyncio
async def test_access_control_outsider(db_session, private_order, outsider):
    """Outsider cannot send messages."""
    service = MessageService(db_session)
    with pytest.raises(PermissionError, match="permission"):
        await service.send_message(
            order_id=private_order.id,
            sender_id=outsider.id,
            content="I'm not involved",
        )


@pytest.mark.asyncio
async def test_get_messages(db_session, private_order, customer, designer):
    """Get paginated messages."""
    service = MessageService(db_session)
    await service.send_message(private_order.id, customer.id, "Msg 1")
    await service.send_message(private_order.id, designer.id, "Msg 2")
    await service.send_message(private_order.id, customer.id, "Msg 3")

    result = await service.get_messages(private_order.id, customer.id)
    assert result.total == 3
    assert len(result.items) == 3
    assert result.items[0].content == "Msg 1"
    assert result.items[2].content == "Msg 3"


@pytest.mark.asyncio
async def test_get_messages_access_control(db_session, private_order, outsider):
    """Outsider cannot read messages."""
    service = MessageService(db_session)
    with pytest.raises(PermissionError, match="access"):
        await service.get_messages(private_order.id, outsider.id)


@pytest.mark.asyncio
async def test_mark_read(db_session, private_order, customer, designer):
    """Mark messages as read marks only messages from other participant."""
    service = MessageService(db_session)
    await service.send_message(private_order.id, designer.id, "Design ready")
    await service.send_message(private_order.id, designer.id, "Check it out")
    await service.send_message(private_order.id, customer.id, "OK")

    unread = await service.get_unread_count(private_order.id, customer.id)
    assert unread == 2

    count = await service.mark_read(private_order.id, customer.id)
    assert count == 2

    unread = await service.get_unread_count(private_order.id, customer.id)
    assert unread == 0


@pytest.mark.asyncio
async def test_send_message_with_file(db_session, private_order, customer):
    """Message can include a file URL."""
    service = MessageService(db_session)
    msg = await service.send_message(
        order_id=private_order.id,
        sender_id=customer.id,
        content="Here's my logo",
        file_url="/uploads/chat/logo.png",
    )
    assert msg.file_url == "/uploads/chat/logo.png"
