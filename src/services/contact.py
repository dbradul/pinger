import copy
import os
import traceback
from datetime import datetime

from dependency_injector.wiring import inject, Provide, Container
from peewee import fn

from common.logger import logger
from common.models import Contact
from services import MessengerBot
from viber.keyboards import *

ADMIN_IDS = os.getenv('ADMIN_IDS').split(',')



# class ContactService:
#
#     def __init__(self, contact_repository):
#         self.contact_repository = contact_repository
#
#     def get_keyboard(self):
#         raise NotImplementedError('get_keyboard method must be implemented')
#
#     def get_admin_keyboard(self):
#         raise NotImplementedError('get_admin_keyboard method must be implemented')
#
#     def subscribe(self):
#         self.contact_repository.active = True
#         self.contact_repository.last_access = datetime.utcnow()
#         self.contact_repository.save()
#
#     def unsubscribe(self):
#         self.contact_repository.active = False
#         self.contact_repository.last_access = datetime.utcnow()
#         self.contact_repository.save()
#
#     def touch(self):
#         self.contact_repository.count_requests += 1
#         self.contact_repository.last_access = datetime.utcnow()
#         self.contact_repository.save()


class ContactService:

    def __init__(self, messenger_bot: MessengerBot):
        self._messenger_bot = messenger_bot

    def get_keyboard(self, contact: Contact):
        raise NotImplementedError('get_keyboard method must be implemented')

    def get_admin_keyboard(self, contact: Contact):
        raise NotImplementedError('get_admin_keyboard method must be implemented')

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

    def notify_subscribers(self, message: str) -> None:
        subscribers = self.get_subscribers(random_sort=True)
        logger.info(f"SUBSCRIBERS TO NOTIFY: {subscribers.count()}")
        for subscriber in subscribers:
            try:
                logger.info(f"  SENDING NOTIFICATION TO CONTACT: {subscriber.name}, {subscriber.id}")
                keyboard = self.get_keyboard(subscriber)
                self._messenger_bot.send_message(subscriber.id, message, keyboard)
                self.touch(subscriber)
            except Exception as e:
                logger.error(f"ERROR SENDING NOTIFICATION TO {subscriber.id}: {e}")
                logger.error(traceback.format_exc())


class ViberContactService(ContactService):

    def get_keyboard(self, contact: Contact):
        if contact and contact.active:
            keyboard = KBRD_UNSUBSCRIBE
        else:
            keyboard = KBRD_SUBSCRIBE

        if contact and contact.id in ADMIN_IDS:
            admin_keyboard = self.get_admin_keyboard(contact)
            keyboard = copy.deepcopy(keyboard)
            keyboard['Buttons'].extend(admin_keyboard)
        return keyboard

    def get_admin_keyboard(self, contact: Contact):
        if self._messenger_bot.masked:
            KBRD_BTN_ADMIN[0]['Text'] = KBRD_BTN_UNMASK_LABEL
            KBRD_BTN_ADMIN[0]['ActionBody'] = MSG_ADMIN_UNMASK_TEXT
        else:
            KBRD_BTN_ADMIN[0]['Text'] = KBRD_BTN_MASK_LABEL
            KBRD_BTN_ADMIN[0]['ActionBody'] = MSG_ADMIN_MASK_TEXT

        if self._messenger_bot.forced_state is None:
            KBRD_BTN_ADMIN[2]['Text'] = KBRD_BTN_FORCED_STATE_ONLINE_LABEL
            KBRD_BTN_ADMIN[2]['ActionBody'] = MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
            KBRD_BTN_ADMIN[3]['Text'] = KBRD_BTN_FORCED_STATE_OFFLINE_LABEL
            KBRD_BTN_ADMIN[3]['ActionBody'] = MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
        elif self._messenger_bot.forced_state is True:
            KBRD_BTN_ADMIN[2]['Text'] = KBRD_BTN_FORCED_STATE_ONLINE_LABEL_DISABLE
            KBRD_BTN_ADMIN[2]['ActionBody'] = MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT
            KBRD_BTN_ADMIN[3]['Text'] = KBRD_BTN_FORCED_STATE_OFFLINE_LABEL
            KBRD_BTN_ADMIN[3]['ActionBody'] = MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
        elif self._messenger_bot.forced_state is False:
            KBRD_BTN_ADMIN[2]['Text'] = KBRD_BTN_FORCED_STATE_ONLINE_LABEL
            KBRD_BTN_ADMIN[2]['ActionBody'] = MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
            KBRD_BTN_ADMIN[3]['Text'] = KBRD_BTN_FORCED_STATE_OFFLINE_LABEL_DISABLE
            KBRD_BTN_ADMIN[3]['ActionBody'] = MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT
        return KBRD_BTN_ADMIN


class TelegramContactService(ContactService):

    def get_keyboard(self, contact):
        ...

    def get_admin_keyboard(self, contact):
        ...
