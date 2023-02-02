from datetime import datetime

from peewee import fn

from common.models import Contact
from services import MessengerBot


class ContactService:

    def __init__(self, messenger_bot: MessengerBot):
        self._messenger_bot = messenger_bot

    def subscribe(self, contact: Contact) -> None:
        contact.active = True
        contact.last_access = datetime.utcnow()
        contact.save()

    def unsubscribe(self, contact: Contact) -> None:
        contact.active = False
        contact.last_access = datetime.utcnow()
        contact.save()

    def increase_requests_counter(self, contact: Contact) -> None:
        contact.count_requests += 1
        contact.save()

    def touch(self, contact: Contact) -> None:
        contact.save()

    def get_recently_active_users(self, limit: int = 10):
        return Contact \
            .filter(Contact.active == True) \
            .order_by(Contact.last_access.desc()) \
            .limit(limit) \
            .objects()

    def get_subscribers(self, random_sort: bool = False):
        # look_back_window = datetime.utcnow() - timedelta(minutes=0)
        contacts = Contact.filter(
            Contact.active == True,
            # Contact.last_access <= look_back_window
        )
        if random_sort:
            contacts = contacts.order_by(fn.Random())
        return contacts.objects()
