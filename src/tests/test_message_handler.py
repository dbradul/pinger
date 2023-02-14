from concurrent.futures import ThreadPoolExecutor

import pytest
from peewee import fn
from unittest.mock import Mock, MagicMock

from common.helpers import TextStyle
from common.models import Contact
from services import ContactService, MessengerBot, MessageHandler, Pinger


@pytest.fixture()
def message_handler(app) -> MessageHandler:
    return app.container.message_handler()


@pytest.fixture(autouse=True)
def populate_db(test_db):
    Contact.insert_many([
        {'id': 1, 'last_access': '2023-01-01', 'name': 'Test User1', 'active': 1, 'count_requests': 0},
        {'id': 2, 'last_access': '2023-01-01', 'name': 'Test User2', 'active': 1, 'count_requests': 1},
        {'id': 3, 'last_access': '2023-01-01', 'name': 'Test User3', 'active': 0, 'count_requests': 0},
        {'id': 4, 'last_access': '2023-01-01', 'name': 'Test User4', 'active': 0, 'count_requests': 1},
    ]).execute()


def test_handle_chat_message(app, message_handler: MessageHandler, random_user: Contact):
    # with app.container.api_client_factory.override(unittest.mock.Mock(ApiClient)):
    #     service2 = container.service_factory()
    #     assert isinstance(service2.api_client, unittest.mock.Mock)
    # message_handler._messenger_bot = Mock(MessengerBot)
    # message_handler._messenger_bot = Mock(spec=MessengerBot)
    # message_handler._messenger_bot = Mock(
    #     get_keyboard=Mock(return_value=['Button1', 'Button2']),
    #     resource=Mock(MSG_QUESTION_TEXT='Світло є?')
    # )

    message_handler._messenger_bot.send_message = Mock()
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

    message_handler._messenger_bot.send_message.assert_called_once_with(
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

    message_handler._messenger_bot.send_message.assert_called_with(
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

    message_handler._messenger_bot.send_message.assert_called_with(
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

    message_handler._messenger_bot.send_message.assert_called_with(
        contact_id=random_user.id,
        message=message_handler._messenger_bot.render_text(
            text='Невідома команда',
            style=TextStyle.ITALIC
        ),
        keyboard=['Button1', 'Button2']
        # keyboard=keyboard
    )