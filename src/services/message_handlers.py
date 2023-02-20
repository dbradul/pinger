import os
import traceback

from datetime import datetime
from viberbot.api.viber_requests import (
    ViberMessageRequest,
    ViberUnsubscribedRequest,
    ViberConversationStartedRequest,
    ViberFailedRequest
)

from common.helpers import TextStyle, ScopeRateLimiter
from common.logger import logger
from common.models import Contact
from . import ContactService, Pinger
from bot import MessengerBot


class MessageHandler:
    def __init__(
            self,
            messenger_bot: MessengerBot,
            contact_service: ContactService,
            pinger: Pinger,
            outliers_filepath: str,
            rate_limit_call_num: int,
            rate_limit_period_sec: int
    ):
        self._contact_service = contact_service
        self._messenger_bot = messenger_bot
        self._pinger = pinger
        self._outliers_filepath = outliers_filepath
        self._rate_limiter = ScopeRateLimiter(
            calls=rate_limit_call_num,
            period=rate_limit_period_sec
        )

    def handle_incoming(self, request_data, request_headers) -> bool:
        raise NotImplementedError('incoming method must be implemented')

    def handle_chat_message(self, message: str, contact: Contact) -> None:
        logger.info(f"MESSAGE: {message}, CONTACT: {contact.id}, {contact.name}")
        keyboard = self._messenger_bot.get_keyboard(contact)
        contact_id = contact.id

        if message == self._messenger_bot.resource.MSG_QUESTION_TEXT:
            self._messenger_bot.send_message(
                contact_id=contact_id,
                message=self._pinger.get_current_state_info(),
                keyboard=keyboard
            )
            self._contact_service.increase_requests_counter(contact)

        elif message == self._messenger_bot.resource.MSG_SUBSCRIBE_TEXT:
            self._contact_service.subscribe(contact)
            keyboard = self._messenger_bot.get_keyboard(contact)
            self._messenger_bot.send_message(
                contact_id=contact_id,
                message='Підписано на розсилку',
                keyboard=keyboard
            )

        elif message == self._messenger_bot.resource.MSG_UNSUBSCRIBE_TEXT:
            self._contact_service.unsubscribe(contact)
            keyboard = self._messenger_bot.get_keyboard(contact)
            self._messenger_bot.send_message(
                contact_id=contact_id,
                message='Відписано від розсилки',
                keyboard=keyboard
            )

        elif message == self._messenger_bot.resource.MSG_ADMIN_STATS_TEXT:
            contacts = self._contact_service.get_recently_active_contacts()
            for contact in contacts:
                self._messenger_bot.send_message(
                    contact_id=contact_id,
                    message=self._messenger_bot.render_text(
                        text=contact.formatted_info(),
                        style=TextStyle.CODE
                    ),
                    keyboard=keyboard
                )

        elif message in (
                self._messenger_bot.resource.MSG_ADMIN_MASK_TEXT,
                self._messenger_bot.resource.MSG_ADMIN_UNMASK_TEXT
        ):
            self._pinger.masked = not self._pinger.masked
            self._messenger_bot.masked = not self._messenger_bot.masked  # FIXME: duplicated info
            keyboard = self._messenger_bot.get_keyboard(contact)
            self._messenger_bot.send_message(
                contact_id=contact_id,
                message=f'Розсилка повідомлень: {"ВИМКНЕНО" if self._pinger.masked else "УВІМКНЕНО"}!',
                keyboard=keyboard
            )

        elif message in (
                self._messenger_bot.resource.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT,
                self._messenger_bot.resource.MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
        ):
            logger.info(f"Enabling forced state: {self._pinger.forced_state}")
            forced_state = message == self._messenger_bot.resource.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
            self._pinger.forced_state = forced_state
            self._messenger_bot.forced_state = forced_state  # FIXME: duplicated info, potential inconsistency
            keyboard = self._messenger_bot.get_keyboard(contact)
            forced_state_str = str(self._pinger.forced_state).upper()
            self._messenger_bot.send_message(
                contact_id=contact_id,
                message=f'Forced state: {forced_state_str}',
                keyboard=keyboard
            )

        elif message in (
                self._messenger_bot.resource.MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT,
                self._messenger_bot.resource.MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT
        ):
            logger.info(f"Disabling forced state: {self._pinger.forced_state}")
            self._pinger.forced_state = None
            self._messenger_bot.forced_state = None  # FIXME: duplicated info, potential inconsistency
            forced_state_str = "DISABLED"
            keyboard = self._messenger_bot.get_keyboard(contact)
            self._messenger_bot.send_message(
                contact_id=contact_id,
                message=f'Forced state: {forced_state_str}',
                keyboard=keyboard
            )

        elif message == self._messenger_bot.resource.MSG_ADMIN_ADV_MESSAGE_TEXT:
            logger.info(f"Sending adv. message...")
            engaged_contacts = self._contact_service.get_engaged_contacts()
            logger.info(f"Contacts to advertise: {engaged_contacts.count()}")
            for engaged_contact in engaged_contacts:
                adv_message = self.prepare_adv_message(engaged_contact)
                keyboard = self._messenger_bot.get_keyboard(contact)
                if adv_message:
                    try:
                        logger.info(f"Sending ADV. message to {engaged_contact.id}, {engaged_contact.name}")
                        self._messenger_bot.send_message(
                            contact_id=engaged_contact.id,
                            message=adv_message,
                            keyboard=keyboard
                        )
                    except Exception as e:
                        logger.error(f"Error sending ADV. message to {engaged_contact.id}: {e}")
                    # logger.error(traceback.format_exc())
                else:
                    logger.error(f"Error preparing ADV. message for {engaged_contact.id}")

        elif message == self._messenger_bot.resource.MSG_ADMIN_FORCED_RESEND_TEXT:
            current_state = self._pinger.get_current_state_info(bot=True)
            failed_outliers = []
            with open(self._outliers_filepath, 'r') as f:
                outliers = f.read().splitlines()
                for outlier in outliers:
                    contact_id = outlier.strip()
                    contact = Contact.get_or_none(Contact.id == contact_id)
                    keyboard = self._messenger_bot.get_keyboard(contact)
                    logger.info(f"RESENDING MESSAGE: {current_state}, CONTACT: {contact.id}")
                    try:
                        self._messenger_bot.send_message(
                            contact_id=contact.id,
                            message=current_state,
                            keyboard=keyboard
                        )
                    except Exception as e:
                        logger.error(f'RESEND FAILED WITH ERROR: {e}')
                        failed_outliers.append(contact_id)
                        logger.error(traceback.format_exc())

            if failed_outliers:
                logger.error(f"DUMPING FAILED OUTLIERS: {len(failed_outliers)} contacts")
            else:
                logger.error(f"RESEND IS SUCCESSFUL! NO FAILED OUTLIERS!")

            with open(self._outliers_filepath, 'w') as f:
                f.write('\n'.join(failed_outliers))

        else:
            self._messenger_bot.send_message(
                contact_id=contact_id,
                message=self._messenger_bot.render_text(
                    text='Невідома команда',
                    style=TextStyle.ITALIC
                ),
                keyboard=keyboard
            )

    def prepare_adv_message(self, contact: Contact) -> str:
        result = ''
        adv_file_path = './data/advertisement.txt'
        if os.path.isfile(adv_file_path):
            with open(adv_file_path, 'r') as f:
                adv_message = f.read()
            invitation = self._contact_service.get_greeting(contact)
            result = adv_message.format(invitation=invitation)
        else:
            logger.error(f"File {adv_file_path} not found!")
        return result

    def get_new_contact_invitation(self, contact: Contact) -> str:
        greeting = self._contact_service.get_greeting(contact)
        invitation = f"{greeting}! 🙌\n\n"
        "Якщо хочете дізнатись чи є світло саме зараз, натисніть кнопку 'Світло є?'\n\n"
        "Якщо хочете отримувати повідомлення про світло, натисніть кнопку 'Підписатись'."
        return invitation


class ViberMessageHandler(MessageHandler):

    def handle_incoming(self, request_data, request_headers) -> bool:
        logger.debug("received request. post data: {0}".format(request_data))

        try:
            # every viber message is signed, you can verify the signature using this method
            # if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
            if not self._messenger_bot.verify_message_signature(request_data, request_headers):
                return False

            # viber_request = viber.parse_request(request.get_data())
            bot_request = self._messenger_bot.parse_request(request_data)

            if isinstance(bot_request, ViberMessageRequest):
                allowed = self._rate_limiter.check_limits(scope=bot_request.sender.id)
                contact = Contact.get_or_none(Contact.id == bot_request.sender.id)
                keyboard = self._messenger_bot.get_keyboard(contact)

                if contact is None:
                    logger.error(f"Contact {bot_request.sender.id} not found in DB!")
                    self._messenger_bot.send_message(
                        contact_id=bot_request.sender.id,
                        message='Ваш контакт не знайдено. Спробуйте видалити чат та додатись до нього знову.'
                    )
                elif not allowed:
                    logger.error(f'RATE LIMIT IS EXCEEDED FOR USER: {bot_request.sender.id}')
                    self._messenger_bot.send_message(
                        contact_id=bot_request.sender.id,
                        message='_Перевищено ліміт запитів. Спробуйте пізніше._',
                        keyboard=keyboard,
                    )
                else:
                    self.handle_chat_message(bot_request.message.text, contact)

            elif isinstance(bot_request, ViberUnsubscribedRequest):
                contact = Contact.get_or_none(Contact.id == bot_request.user_id)
                if contact:
                    logger.error(f'USER LEFT THE CHAT, DELETING: {contact}')
                    contact.delete_instance()

            elif isinstance(bot_request, ViberConversationStartedRequest):
                contact = Contact.get_or_none(Contact.id == bot_request.user.id)
                keyboard = self._messenger_bot.get_keyboard(contact)
                if contact is None:
                    contact = Contact.create(
                        id=bot_request.user.id,
                        name=bot_request.user.name,
                        active=False,
                        last_access=datetime.utcnow()
                    )
                    invitation = self.get_new_contact_invitation(contact)
                    self._messenger_bot.send_message(
                        contact_id=bot_request.user.id,
                        # contact_id=contact.id,
                        message=invitation,
                        keyboard=keyboard
                    )

            elif isinstance(bot_request, ViberFailedRequest):
                logger.warning("Client failed to receive message. Failure: {0}".format(bot_request))

        except Exception as e:
            logger.error(f'GENERAL ERROR: {e}')
            logger.error(traceback.format_exc())

        return True

    def get_new_contact_invitation(self, contact) -> str:
        base_invitation = super().get_new_contact_invitation(contact)
        full_invitation = f"{base_invitation}\n\n"
        """
️👇 ВАЖЛИВО! 👇

Через обмеження у Вайбері з часом можуть перестати приходити повідомлення про вмикання/вимикання світла.

Обмеження стосуються повідомлень від самого бота, але не відповідей користувачеві. Тобто кнопка “Світло є?” буде працювати як зазвичай.

Єдиний спосіб обійти ці обмеження - це змінити месенджер.

Тому, якщо ви зацікавлені стабільно отримувати повідомлення про світло, можна підключитись до бота в Телеграм.

Бот в Вайбері продовжить працювати як звичайно.

Посилання: https://t.me/gem04_bot"""
        return full_invitation


class TelegramMessageHandler(MessageHandler):

    def handle_incoming(self, request_data, request_headers) -> bool:
        logger.debug("received request. post data: {0}".format(request_data))

        try:
            # every viber message is signed, you can verify the signature using this method
            # if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
            if not self._messenger_bot.verify_message_signature(request_data, request_headers):
                return True

            bot_request = self._messenger_bot.parse_request(request_data)
            message_text = bot_request.message and bot_request.message.text
            user_id = bot_request.effective_user.id

            # if ( message_text
            #         and message_text == '/start'
            # ) or ( bot_request.my_chat_member
            #         and bot_request.my_chat_member.new_chat_member.status in ('member')
            #         and bot_request.my_chat_member.old_chat_member.status in ('left', 'kicked')
            # ):
            if (message_text and message_text == '/start'):
                contact = Contact.get_or_none(Contact.id == user_id)
                keyboard = self._messenger_bot.get_keyboard(contact)

                if contact is None:
                    # username = bot_request.message.from_user.full_name
                    contact = Contact.create(
                        id=user_id,
                        name=bot_request.effective_user.full_name,
                        active=False,
                        last_access=datetime.utcnow()
                    )
                    # username = bot_request.effective_user.full_name
                    # invitation =  'Вітаю' if username == 'Subscriber' else \
                    #              f'Вітаю, {username}'
                    # invitation_message = f"{invitation}! 🙌\n\n" \
                    #              "Якщо хочете дізнатись чи є світло саме зараз, натисніть кнопку 'Світло є?'\n\n" \
                    #              "Якщо хочете отримувати повідомлення про світло, натисніть кнопку 'Підписатись'."
                    invitation = self.get_new_contact_invitation(contact)
                    self._messenger_bot.send_message(
                        contact_id=user_id,
                        # message=invitation_message,
                        message=invitation,
                        keyboard=keyboard
                    )
                else:
                    self._messenger_bot.send_message(
                        contact_id=user_id,
                        message=f'Вітаю, {contact.name}! 🙌',
                        keyboard=keyboard
                    )

            elif bot_request.my_chat_member and bot_request.my_chat_member.new_chat_member.status in ('left', 'kicked'):
                contact = Contact.get_or_none(Contact.id == user_id)
                if contact:
                    logger.error(f'USER LEFT THE CHAT, DELETING: {contact}')
                    contact.delete_instance()
            # else:
            #     messenger_bot.send_message(
            #         contact_id=user_id,
            #         message=message_text
            #     )

            # elif bot_request.my_chat_member and bot_request.my_chat_member.new_chat_member.status in ('member'):
            #     pass
            elif message_text and message_text != '/start':
                allowed = self._rate_limiter.check_limits(scope=user_id)
                contact = Contact.get_or_none(Contact.id == user_id)
                keyboard = self._messenger_bot.get_keyboard(contact)

                if contact is None:
                    logger.error(f"Contact {user_id} not found in DB!")
                    self._messenger_bot.send_message(
                        contact_id=user_id,
                        message='Ваш контакт не знайдено. Спробуйте видалити чат та додатись до нього знову.'
                    )
                elif not allowed:
                    logger.error(f'RATE LIMIT IS EXCEEDED FOR USER: {user_id}')
                    self._messenger_bot.send_message(
                        contact_id=user_id,
                        message=self._messenger_bot.render_text(
                            text='Перевищено ліміт запитів. Спробуйте пізніше.',
                            style=TextStyle.ITALIC
                        ),
                        keyboard=keyboard
                    )
                else:
                    self.handle_chat_message(bot_request.message.text, contact)

            elif bot_request.message and (
                    bot_request.message.animation is not None or
                    bot_request.message.audio is not None or
                    bot_request.message.document is not None or
                    bot_request.message.photo is not None or
                    bot_request.message.sticker is not None or
                    bot_request.message.video is not None or
                    bot_request.message.video_note is not None or
                    bot_request.message.voice is not None
            ):
                logger.error(f'UNSUPPORTED MESSAGE TYPE from {user_id}')
                self._messenger_bot.send_message(
                    contact_id=user_id,
                    message=self._messenger_bot.render_text(
                        text='Невідома команда',
                        style=TextStyle.ITALIC
                    )
                )

        except Exception as e:
            logger.error(f'GENERAL ERROR: {e}')
            logger.error(traceback.format_exc())

        return True
