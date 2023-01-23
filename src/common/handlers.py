import datetime
import re
import traceback
from datetime import datetime
from flask import request, Response
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest, ViberUnsubscribedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest

from common.helpers import ScopeRateLimiter
# from app import create_app
from common.logger import logger
from common.models import Contact, History
from common.pinger import Pinger
# from viber.bot import viber
from viber.bot import ViberBot
from viber.keyboards import *

rate_limiter = ScopeRateLimiter(calls=5, period=10)
viber = ViberBot()
pinger = Pinger()


# @app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))

    try:
        # every viber message is signed, you can verify the signature using this method
        if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
            return Response(status=403)

        viber_request = viber.parse_request(request.get_data())

        if isinstance(viber_request, ViberMessageRequest):
            allowed = rate_limiter.check_limits(scope=viber_request.sender.id)
            contact = Contact.get_or_none(Contact.id == viber_request.sender.id)
            keyboard = viber.get_contact_keyboard(contact)

            if contact is None:
                logger.error(f"Contact {viber_request.sender.id} not found in DB!")
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(
                        text='Ваш контакт не знайдено. Спробуйте видалити чат та додатись до нього знову.',
                        # keyboard=keyboard
                    )
                ])
            elif not allowed:
                logger.error(f'RATE LIMIT IS EXCEEDED FOR USER: {viber_request.sender.id}')
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(
                        text='_Перевищено ліміт повідомлень. Спробуйте пізніше._',
                        keyboard=keyboard
                    )
                ])
            else:
                _handle_message(viber_request, contact, keyboard)

        elif isinstance(viber_request, ViberUnsubscribedRequest):
            contact = Contact.get_or_none(Contact.id == viber_request.user_id)
            if contact:
                contact.delete_instance()

        elif isinstance(viber_request, ViberConversationStartedRequest):
            contact = Contact.get_or_none(Contact.id == viber_request.user.id)
            if contact is None:
                username = viber_request.user.name
                invitation =  'Вітаю' if username == 'Subscriber' else \
                             f'Вітаю, {viber_request.user.name}'

                viber.send_messages(viber_request.user.id, [
                    TextMessage(
                        text=f"{invitation}! 🙌\n\n"
                             "Якщо хочете дізнатись чи є світло саме зараз, натисніть кнопку 'Світло є?'\n"
                             "Якщо хочете отримувати повідомлення про світло, натисніть кнопку 'Підписатись'.",
                        keyboard=KBRD_SUBSCRIBE
                    )
                ])
                Contact.create(
                    id=viber_request.user.id,
                    name=viber_request.user.name,
                    active=False,
                    last_access=datetime.utcnow()
                )
        elif isinstance(viber_request, ViberFailedRequest):
            logger.warning("client failed receiving message. failure: {0}".format(viber_request))

    except Exception as e:
        logger.error(f'GENERAL ERROR: {e}')
        logger.error(traceback.format_exc())

    return Response(status=200)


def _handle_message(viber_request, contact, keyboard):
    # global g_is_masked
    message = viber_request.message
    logger.info(f"MESSAGE: {message.text}, CONTACT: {contact.id}")

    if message.text == MSG_QUESTION_TEXT:
        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                # text=viber.current_state_info,
                text=pinger.get_current_state_info(),
                keyboard=keyboard
            )
        ])
        contact.count_requests += 1
        contact.last_access = datetime.utcnow()
        contact.save()
    elif message.text == MSG_SUBSCRIBE_TEXT:
        contact.active = True
        contact.last_access = datetime.utcnow()
        contact.save()
        keyboard = viber.get_contact_keyboard(contact)

        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                text='Підписано на розсилку',
                keyboard=keyboard
            )
        ])
    elif message.text == MSG_UNSUBSCRIBE_TEXT:
        contact.active = False
        contact.last_access = datetime.utcnow()
        contact.save()
        keyboard = viber.get_contact_keyboard(contact)

        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                text='Відписано від розсилки',
                keyboard=keyboard
            )
        ])
    elif message.text == MSG_ADMIN_STATS_TEXT:
        contacts = Contact.filter(Contact.active == True).order_by(Contact.last_access.desc()).objects()
        # result = '\n'.join([c.info() for c in contacts])
        for c in contacts:
            message = f'```{c.formatted_info()}```'
            viber.send_messages(viber_request.sender.id, [
                TextMessage(
                    text=message,
                    keyboard=keyboard
                )
            ])
    elif message.text in (MSG_ADMIN_MASK_TEXT, MSG_ADMIN_UNMASK_TEXT):
        # g_is_masked = not g_is_masked
        # viber.is_masked = not viber.is_masked
        pinger.masked = not pinger.masked
        keyboard = viber.get_contact_keyboard(contact)
        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                # text=f'Розсилка повідомлень: {"ВИМКНЕНО" if viber.is_masked else "УВІМКНЕНО"}!',
                text=f'Розсилка повідомлень: {"ВИМКНЕНО" if pinger.masked else "УВІМКНЕНО"}!',
                keyboard=keyboard
            )
        ])
    return True


# @app.route('/register', methods=['GET'])
def register():
    logger.debug("Registering")

    log_path = '/app/logs/ngrok.log'
    with open(log_path) as f:
        # content = f.read()
        for line in f.readlines():
                m = re.match('.*msg="started tunnel" .*url=https://(.*)$', line)
                if m:
                    try:
                        ngrok_url = m.groups(0)[0]
                        viber.set_webhook('https://' + ngrok_url)
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

#
# def dump_event(current_state_info):
#     History.create(event_date=datetime.utcnow(), event_type=current_state_info)
#
#
# def notify_subscribers(current_state_info):
#     look_back_window = datetime.utcnow() - timedelta(minutes=0)
#     contacts = Contact.filter(Contact.active == True, Contact.last_access <= look_back_window).objects()
#     logger.info(f"SUBSCRIBERS TO NOTIFY: {contacts.count()}")
#     # for i in range(100):
#     for contact in contacts:
#         try:
#             logger.info(f"  SENDING NOTIFICATION TO CONTACT: {contact.name}, {contact.id}")
#             keyboard = viber.get_contact_keyboard(contact)
#             viber.send_messages(contact.id, [
#                 TextMessage(
#                     # text=get_current_state_info(current_state, bot=True) + f" ({i})",
#                     text=current_state_info,
#                     keyboard=keyboard
#                 )
#             ])
#             contact.last_access = datetime.utcnow()
#             contact.save()
#         except Exception as e:
#             logger.error(f"ERROR SENDING MESSAGE TO {contact.id}: {e}")
#             logger.error(traceback.format_exc())
