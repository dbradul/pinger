import json
from typing import Union

import telegram
import viberbot
from viberbot.api.messages import TextMessage

from common.helpers import TextStyle
from common.logger import logger


class MessengerBot:
    def __init__(
            self,
            api_client: Union[viberbot.Api, telegram.Bot]
    ):
        self._api_client = api_client
        self.masked = False
        self.forced_state = None

    def send_message(self, contact_id, message, keyboard=None) -> None:
        raise NotImplementedError('send_message method must be implemented')

    def parse_request(self, data: bytes):
        raise NotImplementedError('parse_request method must be implemented')

    def set_webhook(self, webhook_url):
        raise NotImplementedError('set_webhook method must be implemented')

    def unset_webhook(self):
        raise NotImplementedError('unset_webhook method must be implemented')

    def verify_message_signature(self, request_data, request_headers):
        raise NotImplementedError('verify_message_signature method must be implemented')

    @classmethod
    def render_text(cls, text: str, style: TextStyle) -> str:
        if style == TextStyle.BOLD:
            return f'*{text}*'
        elif style == TextStyle.ITALIC:
            return f'_{text}_'
        elif style == TextStyle.CODE:
            return f'`{text}`'
        else:
            return text


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

    def verify_message_signature(self, request_data, request_headers):
        return self._api_client.verify_signature(request_data, request_headers.get('X-Viber-Content-Signature'))

    def parse_request(self, data: bytes):
        return self._api_client.parse_request(data)

    @classmethod
    def render_text(cls, text: str, style: TextStyle) -> str:
        if style == TextStyle.CODE:
            return f'```{text}```'
        else:
            return super(cls, cls).render_text(text, style)


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

    def verify_message_signature(self, request_data, request_headers):
        return True

    def parse_request(self, data: bytes):
        json_data = json.loads(data.decode())
        return telegram.Update.de_json(json_data, self._api_client)
