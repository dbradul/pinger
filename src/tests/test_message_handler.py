from concurrent.futures import ThreadPoolExecutor

import pytest
from peewee import fn
from unittest.mock import Mock, call, patch

from common.helpers import TextStyle
from common.models import Contact
from services import ContactService, MessengerBot, MessageHandler, Pinger


@pytest.fixture()
def message_handler(app) -> MessageHandler:
    return app.container.message_handler()


# @pytest.fixture(autouse=True)
# def populate_db(test_db):
#     Contact.insert_many([
#         {'id': 1, 'last_access': '2023-01-01', 'name': 'Test User1', 'active': 1, 'count_requests': 0},
#         {'id': 2, 'last_access': '2023-01-01', 'name': 'Test User2', 'active': 1, 'count_requests': 1},
#         {'id': 3, 'last_access': '2023-01-01', 'name': 'Test User3', 'active': 0, 'count_requests': 0},
#         {'id': 4, 'last_access': '2023-01-01', 'name': 'Test User4', 'active': 0, 'count_requests': 1},
#     ]).execute()


@pytest.fixture()
def contact_service(app) -> ContactService:
    return app.container.contact_service()


@pytest.fixture()
def send_message_mock():
    with patch("services.message_handlers.MessengerBot.send_message", autospec=True) as m:
    # with patch("services.messenger_bot.MessengerBot.send_message", autospec=True) as m:
        yield m
#
#
# @pytest.fixture(autouse=True)
# def keyboard_mock():
#     with patch("services.message_handlers.MessengerBot.get_keyboard",
#                autospec=True,
#                return_value=['Button1', 'Button2']) as m:
#         yield m

# @patch('services.messenger_bot.MessengerBot.send_message', autospec=True)
# @patch('services.messenger_bot.MessengerBot.get_keyboard', autospec=True, return_value=['Button1', 'Button2'])
def test_handle_chat_message(
        message_handler: MessageHandler,
        random_user: Contact,
):
    send_message_mock = message_handler._messenger_bot.send_message = Mock()
    message_handler._messenger_bot.get_keyboard = Mock(return_value=['Button1', 'Button2'])
    # keyboard = message_handler._messenger_bot.get_keyboard(random_user)

    # message_handler._pinger = Mock(spec=Pinger)
    # message_handler._pinger.get_current_state_info.return_value = 'Світло є'
    current_state = message_handler._pinger.get_current_state_info()

    # KNOWN messages
    message_handler.handle_chat_message(
        message='Світло є?',
        contact=random_user
    )

    # message_handler._messenger_bot.send_message.assert_called_once_with(
    send_message_mock.assert_called_once_with(
        contact_id=random_user.id,
        # message='Світло є',
        message=current_state,
        keyboard=['Button1', 'Button2']
        # keyboard=keyboard
    )

    # Subscribe
    message_handler.handle_chat_message(
        message=message_handler._messenger_bot.resource.MSG_SUBSCRIBE_TEXT,
        contact=random_user
    )

    send_message_mock.assert_called_with(
        contact_id=random_user.id,
        message='Підписано на розсилку',
        keyboard=['Button1', 'Button2']
        # keyboard=keyboard
    )

    assert random_user.active == 1

    # Unsubscribe
    message_handler.handle_chat_message(
        message=message_handler._messenger_bot.resource.MSG_UNSUBSCRIBE_TEXT,
        contact=random_user
    )

    send_message_mock.assert_called_with(
        contact_id=random_user.id,
        message='Відписано від розсилки',
        keyboard=['Button1', 'Button2']
        # keyboard=keyboard
    )

    assert random_user.active == 0

    # UNKNOWN messages
    message_handler.handle_chat_message(
        message='Hello',
        contact=random_user
    )

    send_message_mock.assert_called_with(
        contact_id=random_user.id,
        message=message_handler._messenger_bot.render_text(
            text='Невідома команда',
            style=TextStyle.ITALIC
        ),
        keyboard=['Button1', 'Button2']
        # keyboard=keyboard
    )


def test_send_adv_message(
        message_handler: MessageHandler,
        contact_service: ContactService,
        random_user: Contact
        # send_message_mock: Mock
    ):
    # Arrange
    send_message_mock = message_handler._messenger_bot.send_message = Mock()

    # Act
    message_handler.handle_chat_message(
        message=message_handler._messenger_bot.resource.MSG_ADMIN_ADV_MESSAGE_TEXT,
        contact=random_user
    )

    # Assert
    calls = [
        call(
            contact_id=engaged_contact.id,
            message=message_handler.prepare_adv_message(engaged_contact),
            keyboard=message_handler._messenger_bot.get_keyboard(random_user)
        )
        for engaged_contact in contact_service.get_engaged_contacts()
    ]

    send_message_mock.assert_has_calls(calls)

    for engaged_contact in contact_service.get_engaged_contacts():
        assert engaged_contact.name in message_handler.prepare_adv_message(engaged_contact)
