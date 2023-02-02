import traceback

from common.logger import logger
from services import MessengerBot
from services.contact import ContactService
from services.history import HistoryService


class PingerListener:
    def __init__(
            self,
            contact_service: ContactService,
            history_service: HistoryService,
            messenger_bot: MessengerBot
    ):
        self._contact_service = contact_service
        self._history_service = history_service
        self._messenger_bot = messenger_bot

    def on_state_change(self, new_state: str):
        subscribers = self._contact_service.get_subscribers(random_sort=True)
        logger.info(f"SUBSCRIBERS TO NOTIFY: {subscribers.count()}")
        for subscriber in subscribers:
            try:
                logger.info(f"  SENDING NOTIFICATION TO CONTACT: {subscriber.name}, {subscriber.id}")
                keyboard = self._messenger_bot.get_keyboard(subscriber)
                self._messenger_bot.send_message(subscriber.id, new_state, keyboard)
                self._contact_service.touch(subscriber)
            except Exception as e:
                logger.error(f"ERROR SENDING NOTIFICATION TO {subscriber.id}: {e}")
                logger.error(traceback.format_exc())


        self._history_service.dump_event(new_state)
