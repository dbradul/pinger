from unittest.mock import Mock, call, patch

import pytest
from flask import Flask
from viberbot.api.viber_requests import ViberConversationStartedRequest, ViberUnsubscribedRequest

from bot import MessengerBot
from common.helpers import TextStyle
from common.models import Contact
from services import ContactService, MessageHandler


@pytest.fixture()
def message_handler(app) -> MessageHandler:
    return app.container.message_handler()


@pytest.fixture()
def messenger_bot(app) -> Mock:
    messenger_bot_mock = Mock(spec=MessengerBot)
    messenger_bot_mock.masked = False
    messenger_bot_mock.forced_state = False
    messenger_bot_mock.get_keyboard = Mock(return_value=['Button1', 'Button2'])
    messenger_bot_mock.verify_message_signature = Mock(return_value=True)
    messenger_bot_mock.send_message = Mock(
        side_effect=lambda *args, **kwargs: print('Sending message...')
    )
    return messenger_bot_mock
    # return app.container.messenger_bot()


@pytest.fixture()
def contact_service(app) -> ContactService:
    contact_service = app.container.contact_service()
    # contact_service = Mock(spec=ContactService)
    contact_service.get_keyboard = Mock(return_value=['Button1', 'Button2'])
    return contact_service


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
            # keyboard=message_handler._messenger_bot.get_keyboard(random_user)
            keyboard=contact_service.get_keyboard(random_user)
        )
        for engaged_contact in contact_service.get_engaged_contacts()
    ]

    send_message_mock.assert_has_calls(calls)

    for engaged_contact in contact_service.get_engaged_contacts():
        assert engaged_contact.name in message_handler.prepare_adv_message(engaged_contact)


def test_user_creation(
        app,
        contact_service: ContactService,
        messenger_bot: Mock,
):
    # Arrange
    all_contacts = list(contact_service.get_all())
    messenger_bot.parse_request = Mock(
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

    # Act
    with app.container.messenger_bot.override(messenger_bot):
        with app.container.contact_service.override(contact_service):
            message_handler = app.container.message_handler()
            message_handler.handle_incoming('42', 42)

    # Assert
    assert len(contact_service.get_all()) == len(all_contacts) + 1
    new_contact = contact_service.get_by_filter(Contact.id == '01234567890A=')[0]
    assert new_contact.name == 'John McClane'
    messenger_bot.send_message.assert_called_once_with(
        contact_id=new_contact.id,
        message=message_handler.get_new_contact_invitation(new_contact),
        keyboard=['Button1', 'Button2']
    )


def test_user_deletion(
        app, ##: Flask,
        contact_service: ContactService,
        messenger_bot: Mock,
):
    # Arrange
    all_contacts = list(contact_service.get_all())
    messenger_bot.parse_request = Mock(
        return_value=ViberUnsubscribedRequest().from_dict({
            'user_id': '1',
            'event': 'unsubscribed',
            'timestamp': 1530000000,
        })
    )

    # Act
    with app.container.messenger_bot.override(messenger_bot):
        message_handler = app.container.message_handler()
        message_handler.handle_incoming('42', 42)

    # Assert
    assert len(contact_service.get_all()) == len(all_contacts) - 1
    deleted_contact = contact_service.get_by_filter(Contact.id == '1')
    assert len(deleted_contact) == 0
