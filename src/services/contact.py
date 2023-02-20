from datetime import datetime

from peewee import fn, ModelSelect
from typing import List

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

    def get_recently_active_contacts(self, limit: int = 10) -> ModelSelect:
        return Contact \
            .filter() \
            .order_by(Contact.last_access.desc()) \
            .limit(limit) \
            .objects()

    def get_subscribers(self, random_sort: bool = False) -> ModelSelect:
        # look_back_window = datetime.utcnow() - timedelta(minutes=0)
        contacts = Contact.filter(
            Contact.active == True,
            # Contact.last_access <= look_back_window
        )
        if random_sort:
            contacts = contacts.order_by(fn.Random())
        return contacts.objects()

    def get_engaged_contacts(self) -> ModelSelect:
        return self.get_by_filter(
            (Contact.active == True) |
            (Contact.count_requests > 0)
        )

    def get_by_filter(self, filter) -> ModelSelect:
        return Contact.select().where(filter).objects()

    def get_all(self) -> ModelSelect:
        return Contact.filter().objects()

    def get_greeting(self, contact: Contact) -> str:
        invitation = (
            'Вітаю' if contact.name == 'Subscriber'
            else f'Вітаю, {contact.name}'
        )
        return invitation
