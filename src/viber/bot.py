import traceback

import copy
from datetime import datetime, timedelta

import os

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage

# from common.handlers import ADMIN_IDS
from common.helpers import Singleton
from common.logger import logger
from common.models import History, Contact
from common.pinger import Pinger
from viber.keyboards import *

VIBER_API_TOKEN = os.getenv('VIBER_API_TOKEN')
ADMIN_IDS = os.getenv('ADMIN_IDS').split(',')

pinger = Pinger()


class ViberBot(Singleton, Api):

    def __init__(self):
        # super().__init__(BotConfiguration(
        #     name='Світло 4-10',
        #     avatar='http://viber.com/avatar.jpg',
        #     auth_token=VIBER_API_TOKEN
        # ))
        self._viber = Api(BotConfiguration(
            name='Світло 4-10',
            avatar='http://site.com/avatar.jpg',
            auth_token=VIBER_API_TOKEN
        ))
        # self.is_masked = False
        self.current_state_info = None

    def __getattr__(self, item):
        return getattr(self._viber, item)

    def get_contact_keyboard(self, contact):
        keyboard = KBRD_UNSUBSCRIBE if (contact and contact.active) else KBRD_SUBSCRIBE
        if contact and contact.id in ADMIN_IDS:
            keyboard = copy.deepcopy(keyboard)
            keyboard['Buttons'].extend(self.get_admin_keyboard())
        return keyboard

    def get_admin_keyboard(self):
        # label, action = [KBRD_BTN_UNMASK_LABEL, MSG_ADMIN_UNMASK_TEXT] if self.is_masked \
        label, action = [KBRD_BTN_UNMASK_LABEL, MSG_ADMIN_UNMASK_TEXT] if pinger.masked \
            else [KBRD_BTN_MASK_LABEL, MSG_ADMIN_MASK_TEXT]
        KBRD_BTN_MASK_UNMASK['Text'] = label
        KBRD_BTN_MASK_UNMASK['ActionBody'] = action
        KBRD_BTN_ADMIN[0] = KBRD_BTN_MASK_UNMASK
        return KBRD_BTN_ADMIN

    def dump_event(self, current_state_info):
        History.create(event_date=datetime.utcnow(), event_type=current_state_info)

    def notify_subscribers(self, current_state_info):
        self.current_state_info = current_state_info
        look_back_window = datetime.utcnow() - timedelta(minutes=0)
        contacts = Contact.filter(Contact.active == True, Contact.last_access <= look_back_window).objects()
        logger.info(f"SUBSCRIBERS TO NOTIFY: {contacts.count()}")
        # for i in range(100):
        for contact in contacts:
            try:
                logger.info(f"  SENDING NOTIFICATION TO CONTACT: {contact.name}, {contact.id}")
                keyboard = self.get_contact_keyboard(contact)
                # self._viber.send_messages(contact.id, [
                self.send_messages(contact.id, [
                    TextMessage(
                        # text=get_current_state_info(current_state, bot=True) + f" ({i})",
                        text=self.current_state_info,
                        keyboard=keyboard
                    )
                ])
                contact.last_access = datetime.utcnow()
                contact.save()
            except Exception as e:
                logger.error(f"ERROR SENDING MESSAGE TO {contact.id}: {e}")
                logger.error(traceback.format_exc())
