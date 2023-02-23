from datetime import datetime

from peewee import fn, ModelSelect
from typing import List, Union

from bot.resources import Resource
from common.models import Contact
from bot import MessengerBot


class ContactService:
    def __init__(
            self,
            messenger_bot: MessengerBot,
            bot_resource: Resource,
            # admin_ids: list[str] = None
    ):
        self._messenger_bot = messenger_bot
        self._bot_resource = bot_resource
        # self._admin_ids = admin_ids or []

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

    def get_keyboard(self, contact: Union[None, Contact]):
        return self._bot_resource.get_keyboard(
            is_admin=contact and contact.admin,
            is_subscribed=contact and contact.active,
            is_masked=self._messenger_bot.masked,
            is_forced_state=self._messenger_bot.forced_state
        )