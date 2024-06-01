import traceback

from bot.resources import Resource
from common.logger import logger
from bot import MessengerBot
from services.contact import ContactService
from services.history import HistoryService


class PingerListener:
    def __init__(
            self,
            contact_service: ContactService,
            history_service: HistoryService,
            messenger_bot: MessengerBot,
            bot_resource: Resource,
            failed_contacts_filepath: str = None
    ):
        self._contact_service = contact_service
        self._history_service = history_service
        self._messenger_bot = messenger_bot
        self._bot_resource = bot_resource
        self._failed_contacts_filepath = failed_contacts_filepath

    def on_state_change(self, new_state: str):
        subscribers = self._contact_service.get_subscribers(random_sort=True)
        failed_subscribers = []
        logger.info(f"SUBSCRIBERS TO NOTIFY: {subscribers.count()}")
        for subscriber in subscribers:
            try:
                logger.info(f"  SENDING NOTIFICATION TO CONTACT: {subscriber.id}, {subscriber.name}")
                keyboard = self._bot_resource.get_keyboard(subscriber, self._messenger_bot)
                self._messenger_bot.send_message(subscriber.id, new_state, keyboard)
                self._contact_service.touch(subscriber)
            except Exception as e:
                logger.error(f"ERROR SENDING NOTIFICATION TO {subscriber.id}: {e}")
                logger.error(traceback.format_exc())
                failed_subscribers.append(subscriber)

        if failed_subscribers:
            logger.error(f"Couldn't send to {len(failed_subscribers)} contacts, dumping to outliers.txt")
            if self._failed_contacts_filepath is not None:
                with open(self._failed_contacts_filepath, 'w+') as f:
                    f.writelines([f'{c.id}\n' for c in failed_subscribers])
        else:
            logger.info("All notifications sent successfully")

        self._history_service.dump_event(new_state)
