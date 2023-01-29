from typing import Any

from viberbot.api.messages import TextMessage

from common.helpers import Singleton, ThreadSafeSingleton


class MessengerBot:

    def __init__(self, api_client: Any = None):
        self._api_client = api_client

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
    pass

