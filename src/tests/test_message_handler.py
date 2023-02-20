from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest
from peewee import fn
from unittest.mock import Mock, call, patch

from viberbot.api.user_profile import UserProfile
from viberbot.api.viber_requests import ViberConversationStartedRequest, ViberUnsubscribedRequest

from common.helpers import TextStyle
from common.models import Contact
from services import ContactService, MessengerBot, MessageHandler, Pinger


@pytest.fixture()
def message_handler(app) -> MessageHandler:
    return app.container.message_handler()


@pytest.fixture()
def messenger_bot(app) -> MessengerBot:
    return app.container.messenger_bot()


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


def test_user_creation(
        message_handler: MessageHandler,
        contact_service: ContactService,
        # messenger_bot: MessengerBot,
):
    # Arrange
    all_contacts = list(contact_service.get_all())

    message_handler._messenger_bot.verify_message_signature = Mock(return_value=True)
    message_handler._messenger_bot.parse_request = Mock(
        return_value=ViberConversationStartedRequest().from_dict({
            'event': 'conversation_started',
            'timestamp': 1530000000,
            'message_token': 4912661846655238145,
            'type': 'open',
            'context': 'context information',
            'user': {
                "id": "01234567890A=",
                "name": "John McClane",
                "avatar": "http://avatar.example.com",
                "country": "UK",
                "language": "en",
                "api_version": 1
            }
        })
    )
    message_handler._messenger_bot.send_message = Mock(
        side_effect=lambda *args, **kwargs: print('Sending message...')
    )

    # Act
    message_handler.handle_incoming(Mock(), Mock())

    # Assert
    assert len(contact_service.get_all()) == len(all_contacts) + 1

    new_contact = contact_service.get_by_filter(Contact.id == '01234567890A=')[0]

    message_handler._messenger_bot.send_message.assert_called_once_with(
        contact_id=new_contact.id,
        message=message_handler.get_new_contact_invitation(new_contact),
        keyboard=message_handler._messenger_bot.get_keyboard(new_contact)
    )


def test_user_deletion(
        message_handler: MessageHandler,
        contact_service: ContactService,
        # messenger_bot: MessengerBot,
):
    # Arrange
    all_contacts = list(contact_service.get_all())

    message_handler._messenger_bot.verify_message_signature = Mock(return_value=True)
    message_handler._messenger_bot.parse_request = Mock(
        return_value=ViberUnsubscribedRequest().from_dict({
            'user_id': '1',
            'event': 'unsubscribed',
            'timestamp': 1530000000,
        })
    )

    # Act
    message_handler.handle_incoming(Mock(), Mock())

    # Assert
    assert len(contact_service.get_all()) == len(all_contacts) - 1
    deleted_contact = contact_service.get_by_filter(Contact.id == '1')
    assert len(deleted_contact) == 0
