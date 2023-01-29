from datetime import datetime, timedelta
import traceback

from services.bot import MessengerBot
from common.helpers import ThreadSafeSingleton
from common.pinger import Pinger
from common.logger import logger
from common.models import History, Contact
from services.contacts import ViberContactService

pinger = Pinger()


class MessengerService(metaclass=ThreadSafeSingleton):
    def __init__(self, backend: MessengerBot = None):
        self._backend = backend

    def send_message(self, contact_id, message):
        self._backend.send_message(contact_id, message)

    def dump_event(self, event_info: str):
        History.create(
            event_date=datetime.utcnow(),
            event_type=event_info
        )

    def on_state_change(self, new_state: str):
        self.current_state_info = new_state
        self.dump_event(new_state)
        look_back_window = datetime.utcnow() - timedelta(minutes=0)
        contacts = Contact.filter(Contact.active == True, Contact.last_access <= look_back_window).objects()
        contact_service = ViberContactService()
        logger.info(f"SUBSCRIBERS TO NOTIFY: {contacts.count()}")
        for contact in contacts:
            try:
                logger.info(f"  SENDING NOTIFICATION TO CONTACT: {contact.name}, {contact.id}")
                keyboard = contact_service.get_keyboard(contact)
                self._backend.send_message(contact.id, self.current_state_info, keyboard)
                contact.last_access = datetime.utcnow()
                contact.save()
            except Exception as e:
                logger.error(f"ERROR SENDING MESSAGE TO {contact.id}: {e}")
                logger.error(traceback.format_exc())
