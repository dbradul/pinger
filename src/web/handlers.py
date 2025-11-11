import datetime
import os
import re
import traceback
from datetime import datetime

from dependency_injector.wiring import Provide, inject
from flask import request, Response
from viberbot.api.viber_requests import ViberConversationStartedRequest, ViberUnsubscribedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest

from app.containers import Container
from common.helpers import ScopeRateLimiter, TextStyle
from common.logger import logger
from common.models import Contact, History
from services import MessengerBot
from services.contact import ContactService
from services.pinger import Pinger

rate_limiter = ScopeRateLimiter(calls=5, period=10)
OUTLIERS_FILEPATH = os.getenv('OUTLIERS_FILEPATH')

# @app.route('/', methods=['POST'])
@inject
def incoming(
        messenger_bot: MessengerBot = Provide[Container.messenger_bot]
):
    logger.debug("received request. post data: {0}".format(request.get_data()))

    try:
        # every viber message is signed, you can verify the signature using this method
        # if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        if not messenger_bot.verify_message_signature(request.get_data(), request.headers):
            return Response(status=403)

        # viber_request = viber.parse_request(request.get_data())
        bot_request = messenger_bot.parse_request(request.get_data())

        if isinstance(bot_request, ViberMessageRequest):
            allowed = rate_limiter.check_limits(scope=bot_request.sender.id)
            contact = Contact.get_or_none(Contact.id == bot_request.sender.id)
            keyboard = messenger_bot.get_keyboard(contact)

            if contact is None:
                logger.error(f"Contact {bot_request.sender.id} not found in DB!")
                messenger_bot.send_message(
                    contact_id=bot_request.sender.id,
                    message='Ваш контакт не знайдено. Спробуйте видалити чат та додатись до нього знову.'
                )
            elif not allowed:
                logger.error(f'RATE LIMIT IS EXCEEDED FOR USER: {bot_request.sender.id}')
                messenger_bot.send_message(
                    contact_id=bot_request.sender.id,
                    message='_Перевищено ліміт запитів. Спробуйте пізніше._',
                    keyboard=keyboard,
                )
            else:
                _handle_chat_message(bot_request.message.text, contact)

        elif isinstance(bot_request, ViberUnsubscribedRequest):
            contact = Contact.get_or_none(Contact.id == bot_request.user_id)
            if contact:
                logger.error(f'USER LEFT THE CHAT, DELETING: {contact}')
                contact.delete_instance()

        elif isinstance(bot_request, ViberConversationStartedRequest):
            contact = Contact.get_or_none(Contact.id == bot_request.user.id)
            keyboard = messenger_bot.get_keyboard(contact)
            if contact is None:
                username = bot_request.user.name
                invitation =  'Вітаю' if username == 'Subscriber' else \
                             f'Вітаю, {bot_request.user.name}'
                messenger_bot.send_message(
                    contact_id=bot_request.user.id,
                    message=f"{invitation}! 🙌\n\n"
                             "Якщо хочете дізнатись чи є світло саме зараз, натисніть кнопку 'Світло є?'\n\n"
                             "Якщо хочете отримувати повідомлення про світло, натисніть кнопку 'Підписатись'."
"""


️👇 ВАЖЛИВО! 👇

Через обмеження у Viber з часом можуть перестати надходити повідомлення про вмикання/вимикання світла.

Обмеження стосуються лише повідомлень від самого бота (push-повідмолення). Кнопка “Світло є?” буде працювати як зазвичай.

Єдиний спосіб обійти ці обмеження - це змінити месенджер.

Якщо ви зацікавлені стабільно отримувати повідомлення про світло, можна підключитись до бота в Телеграм.

Посилання: https://t.me/gem04_bot"""
                    ,
                    keyboard=keyboard
                )
                Contact.create(
                    id=bot_request.user.id,
                    name=bot_request.user.name,
                    active=False,
                    last_access=datetime.utcnow()
                )
        elif isinstance(bot_request, ViberFailedRequest):
            logger.warning("Client failed to receive message. Failure: {0}".format(bot_request))

    except Exception as e:
        logger.error(f'GENERAL ERROR: {e}')
        logger.error(traceback.format_exc())

    return Response(status=200)


# @app.route('/', methods=['POST'])
@inject
def incoming_tg(
        messenger_bot: MessengerBot = Provide[Container.messenger_bot]
):
    logger.debug("received request. post data: {0}".format(request.get_data()))

    try:
        # every viber message is signed, you can verify the signature using this method
        # if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        if not messenger_bot.verify_message_signature(request.get_data(), request.headers):
            return Response(status=403)

        bot_request = messenger_bot.parse_request(request.get_data())
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
            keyboard = messenger_bot.get_keyboard(contact)

            if contact is None:
                # username = bot_request.message.from_user.full_name
                username = bot_request.effective_user.full_name
                invitation =  'Вітаю' if username == 'Subscriber' else \
                             f'Вітаю, {username}'
                invitation_message = f"{invitation}! 🙌\n\n" \
                             "Якщо хочете дізнатись чи є світло саме зараз, натисніть кнопку 'Світло є?'\n\n" \
                             "Якщо хочете отримувати повідомлення про світло, натисніть кнопку 'Підписатись'."
                messenger_bot.send_message(
                    contact_id=user_id,
                    message=invitation_message,
                    keyboard=keyboard
                )
                Contact.create(
                    id=user_id,
                    name=username,
                    active=False,
                    last_access=datetime.utcnow()
                )
            else:
                messenger_bot.send_message(
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
            allowed = rate_limiter.check_limits(scope=user_id)
            contact = Contact.get_or_none(Contact.id == user_id)
            keyboard = messenger_bot.get_keyboard(contact)

            if contact is None:
                logger.error(f"Contact {user_id} not found in DB!")
                messenger_bot.send_message(
                    contact_id=user_id,
                    message='Ваш контакт не знайдено. Спробуйте видалити чат та додатись до нього знову.'
                )
            elif not allowed:
                logger.error(f'RATE LIMIT IS EXCEEDED FOR USER: {user_id}')
                messenger_bot.send_message(
                    contact_id=user_id,
                    message=messenger_bot.render_text(
                        text='Перевищено ліміт запитів. Спробуйте пізніше.',
                        style=TextStyle.ITALIC
                    ),
                    keyboard=keyboard
                )
            else:
                _handle_chat_message(bot_request.message.text, contact)

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
            messenger_bot.send_message(
                contact_id=user_id,
                message=messenger_bot.render_text(
                    text='Невідома команда',
                    style=TextStyle.ITALIC
                )
            )

    except Exception as e:
        logger.error(f'GENERAL ERROR: {e}')
        logger.error(traceback.format_exc())

    return Response(status=200)


@inject
def _handle_chat_message(
        message: str,
        contact: Contact,
        contact_service: ContactService = Provide[Container.contact_service],
        messenger_bot: MessengerBot = Provide[Container.messenger_bot],
        pinger: Pinger = Provide[Container.pinger],
) -> None:
    logger.info(f"MESSAGE: {message}, CONTACT: {contact.id}, {contact.name}")
    keyboard = messenger_bot.get_keyboard(contact)
    contact_id = contact.id

    if message == messenger_bot.resource.MSG_QUESTION_TEXT:
        messenger_bot.send_message(
            contact_id=contact_id,
            message=pinger.get_current_state_info(),
            keyboard=keyboard
        )
        contact_service.increase_requests_counter(contact)

    elif message == messenger_bot.resource.MSG_SUBSCRIBE_TEXT:
        contact_service.subscribe(contact)
        keyboard = messenger_bot.get_keyboard(contact)
        messenger_bot.send_message(
            contact_id=contact_id,
            message='Підписано на розсилку',
            keyboard=keyboard
        )

    elif message == messenger_bot.resource.MSG_UNSUBSCRIBE_TEXT:
        contact_service.unsubscribe(contact)
        keyboard = messenger_bot.get_keyboard(contact)
        messenger_bot.send_message(
            contact_id=contact_id,
            message='Відписано від розсилки',
            keyboard=keyboard
        )

    elif message == messenger_bot.resource.MSG_ADMIN_STATS_TEXT:
        contacts = contact_service.get_recently_active_contacts()
        for contact in contacts:
            messenger_bot.send_message(
                contact_id=contact_id,
                message=messenger_bot.render_text(
                    text=contact.formatted_info(),
                    style=TextStyle.CODE
                ),
                keyboard=keyboard
            )

    elif message in (messenger_bot.resource.MSG_ADMIN_MASK_TEXT, messenger_bot.resource.MSG_ADMIN_UNMASK_TEXT):
        pinger.masked = not pinger.masked
        messenger_bot.masked = not messenger_bot.masked  # FIXME: duplicated info
        keyboard = messenger_bot.get_keyboard(contact)
        messenger_bot.send_message(
            contact_id=contact_id,
            message=f'Розсилка повідомлень: {"ВИМКНЕНО" if pinger.masked else "УВІМКНЕНО"}!',
            keyboard=keyboard
        )

    elif message in (
            messenger_bot.resource.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT,
            messenger_bot.resource.MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
    ):
        logger.info(f"Enabling forced state: {pinger.forced_state}")
        pinger.forced_state = message == messenger_bot.resource.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
        messenger_bot.forced_state = message == messenger_bot.resource.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT # FIXME: duplicated info
        keyboard = messenger_bot.get_keyboard(contact)
        forced_state_str = "DISABLED" if pinger.forced_state is None else str(pinger.forced_state).upper()
        messenger_bot.send_message(
            contact_id=contact_id,
            message=f'Forced state: {forced_state_str}',
            keyboard=keyboard
        )

    elif message in (
            messenger_bot.resource.MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT,
            messenger_bot.resource.MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT
    ):
        logger.info(f"Disabling forced state: {pinger.forced_state}")
        pinger.forced_state = None
        messenger_bot.forced_state = None   # FIXME: duplicated info
        forced_state_str = "DISABLED" if pinger.forced_state is None else str(pinger.forced_state).upper()
        keyboard = messenger_bot.get_keyboard(contact)
        messenger_bot.send_message(
            contact_id=contact_id,
            message=f'Forced state: {forced_state_str}',
            keyboard=keyboard
        )

    elif message == messenger_bot.resource.MSG_ADMIN_ADV_MESSAGE_TEXT:
        invitation = ('Вітаю' if contact.name == 'Subscriber'
                      else f'Вітаю, {contact.name}')
        adv_message = f'''{invitation}!

Через обмеження у Вайбері найближчим часом можуть перестати приходити повідомлення про вмикання/вимикання світла.

Обмеження стосуються повідомлень від самого бота, але не відповідей користувачеві. Тобто кнопка “Світло є?” буде працювати як зазвичай.

Єдиний спосіб обійти ці обмеження - це змінити месенджер.

Тому, якщо ви зацікавлені стабільно отримувати повідомлення про світло, можна підключитись до бота в Телеграм.

Бот в Вайбері продовжить працювати як звичайно.

Посилання: https://t.me/gem04_bot
        '''
        logger.info(f"Sending adv. message...")
        # all_contacts = contact_service.get_all()
        engaged_contacts = contact_service.get_engaged_contacts()
        logger.info(f"Contacts to advertise: {engaged_contacts.count()}")
        for contact in engaged_contacts:
            keyboard = messenger_bot.get_keyboard(contact)
            try:
                logger.info(f"Sending ADV. message to {contact.id}, {contact.name}")
                messenger_bot.send_message(
                    contact_id=contact.id,
                    message=adv_message,
                    keyboard=keyboard
                )
            except Exception as e:
                logger.error(f"Error sending ADV. message to {contact.id}: {e}")
                # logger.error(traceback.format_exc())

    elif message == messenger_bot.resource.MSG_ADMIN_FORCED_RESEND_TEXT:
        current_state = pinger.get_current_state_info(bot=True)
        failed_outliers = []
        with open(OUTLIERS_FILEPATH, 'r') as f:
            outliers = f.read().splitlines()
            for outlier in outliers:
                contact_id = outlier.strip()
                contact = Contact.get_or_none(Contact.id == contact_id)
                keyboard = messenger_bot.get_keyboard(contact)
                logger.info(f"RESENDING MESSAGE: {current_state}, CONTACT: {contact.id}")
                try:
                    messenger_bot.send_message(
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

        with open(OUTLIERS_FILEPATH, 'w') as f:
            f.write('\n'.join(failed_outliers))

    else:
        messenger_bot.send_message(
            contact_id=contact_id,
            message=messenger_bot.render_text(
                text='Невідома команда',
                style=TextStyle.ITALIC
            ),
            keyboard=keyboard
        )



# @app.route('/register', methods=['GET'])
@inject
def register(
    messenger_bot: MessengerBot = Provide[Container.messenger_bot]
):
    logger.debug("Registering")
    log_path = '/app/logs/ngrok.log'
    with open(log_path) as f:
        for line in f.readlines():
            m = re.match('.*msg="started tunnel" .*url=https://(.*)$', line)
            if m:
                try:
                    ngrok_url = m.groups(0)[0]
                    messenger_bot.set_webhook('https://' + ngrok_url)
                    logger.info(f"SELF REGISTERING DONE: {ngrok_url}")
                    break
                except Exception as e:
                    logger.error(f"SELF REGISTERING ERROR: {e}")
                    logger.error(traceback.format_exc())
        else:
            logger.error('URL IS NOT RECOGNIZED')

    return 'OK - Registered'


# @app.route('/init_db', methods=['GET'])
def init_db():
    logger.debug("received request. get data: {0}".format(request.get_data()))
    Contact.create_table()
    History.create_table()
    return 'OK - Created'
