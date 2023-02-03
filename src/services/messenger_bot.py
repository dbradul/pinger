import json
from typing import Any, Union

import telegram
import viberbot
from viberbot.api.messages import TextMessage

from bot.resources import Resource
from common.helpers import TextStyle
from common.logger import logger
from common.models import Contact


class MessengerBot:
    def __init__(
            self,
            api_client: Union[viberbot.Api, telegram.Bot],
            resource: Resource,
            admin_ids: list[str] = None
    ):
        self._api_client = api_client
        self.resource = resource
        self.masked = False
        self.forced_state = None
        self._admin_ids = admin_ids or []

    def send_message(self, contact_id, message, keyboard=None):
        raise NotImplementedError('send_message method must be implemented')

    def parse_request(self, data):
        raise NotImplementedError('parse_request method must be implemented')

    def set_webhook(self, webhook_url):
        raise NotImplementedError('set_webhook method must be implemented')

    def unset_webhook(self):
        raise NotImplementedError('unset_webhook method must be implemented')

    def verify_message_signature(self, signature, data):
        raise NotImplementedError('verify_message_signature method must be implemented')

    @staticmethod
    def render_text(text: str, style: TextStyle) -> str:
        if style == TextStyle.BOLD:
            return f'*{text}*'
        elif style == TextStyle.ITALIC:
            return f'_{text}_'
        elif style == TextStyle.CODE:
            return f'`{text}`'
        else:
            return text

    def get_keyboard(self, contact: Union[None, Contact]):
        # is_admin = contact and contact.id in self._admin_ids
        # is_subscribed = contact and contact.active
        # is_masked = self._messenger_bot.masked
        # is_forced_state = self._messenger_bot.forced_state
        return self.resource.get_keyboard(
            is_admin=contact and contact.id in self._admin_ids,
            is_subscribed=contact and contact.active,
            is_masked=self.masked,
            is_forced_state=self.forced_state
        )


class ViberMessengerBot(MessengerBot):
    def send_message(self, contact_id, message, keyboard=None):
        self._api_client.send_messages(contact_id, [
            TextMessage(
                text=message,
                keyboard=keyboard
            )
        ])

    def set_webhook(self, webhook_url):
        self._api_client.set_webhook(webhook_url)

    def verify_message_signature(self, data, signature):
        return self._api_client.verify_signature(data, signature)

    def parse_request(self, data):
        return self._api_client.parse_request(data)


class TelegramMessengerBot(MessengerBot):
    def send_message(self, contact_id, message, keyboard=None):
        self._api_client.sendMessage(
            chat_id=contact_id,
            text=message,
            reply_markup=keyboard,
            parse_mode='markdown'
        )

    def set_webhook(self, webhook_url):
        logger.info('Setting webhook to %s', webhook_url)
        self._api_client.setWebhook(webhook_url)

    def verify_message_signature(self, data, signature):
        return True

    def parse_request(self, data):
        # json_data = telegram.utils.request.Request.de_json(data, self._api_client)
        json_data = json.loads(data.decode())
        return telegram.Update.de_json(json_data, self._api_client)
