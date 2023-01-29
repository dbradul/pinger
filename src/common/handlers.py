import datetime
import re
import traceback
from datetime import datetime
from flask import request, Response
from viberbot.api.viber_requests import ViberConversationStartedRequest, ViberUnsubscribedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest

from dependency_injector.wiring import Provide, inject
from pinger.containers import Container


# from services.backends import ViberBotBackend
from common.helpers import ScopeRateLimiter
# from app import create_app
from common.logger import logger
from common.models import Contact, History
from common.pinger import Pinger
from services import MessengerBot
from services.contacts import ContactService
from services.messengers import MessengerService
# from viber.bot import viber
# from viber.bot import ViberBot
from viber.keyboards import *

rate_limiter = ScopeRateLimiter(calls=5, period=10)
# viber = ViberBot()
# viber = ViberBotBackend()
# messenger = MessengerService()
pinger = Pinger()




# @app.route('/', methods=['POST'])
@inject
def incoming(
        messenger_bot: MessengerBot = Provide[Container.messenger_bot]
):
    logger.debug("received request. post data: {0}".format(request.get_data()))

    try:
        # every viber message is signed, you can verify the signature using this method
        # if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        if not messenger_bot.verify_message_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
            return Response(status=403)

        # viber_request = viber.parse_request(request.get_data())
        viber_request = messenger_bot.parse_request(request.get_data())

        if isinstance(viber_request, ViberMessageRequest):
            allowed = rate_limiter.check_limits(scope=viber_request.sender.id)
            contact = Contact.get_or_none(Contact.id == viber_request.sender.id)

            if contact is None:
                logger.error(f"Contact {viber_request.sender.id} not found in DB!")
                messenger_bot.send_message(
                    contact_id=viber_request.sender.id,
                    message='Ваш контакт не знайдено. Спробуйте видалити чат та додатись до нього знову.'
                )
            elif not allowed:
                logger.error(f'RATE LIMIT IS EXCEEDED FOR USER: {viber_request.sender.id}')
                messenger_bot.send_message(
                    contact_id=viber_request.sender.id,
                    message='_Перевищено ліміт повідомлень. Спробуйте пізніше._'
                )
            else:
                # _handle_message(viber_request, contact, keyboard, contact_service)
                _handle_message(viber_request, contact)

        elif isinstance(viber_request, ViberUnsubscribedRequest):
            contact = Contact.get_or_none(Contact.id == viber_request.user_id)
            if contact:
                logger.error(f'USER LEFT THE CHAT, DELETING: {contact}')
                contact.delete_instance()

        elif isinstance(viber_request, ViberConversationStartedRequest):
            contact = Contact.get_or_none(Contact.id == viber_request.user.id)
            if contact is None:
                username = viber_request.user.name
                invitation =  'Вітаю' if username == 'Subscriber' else \
                             f'Вітаю, {viber_request.user.name}'
                messenger_bot.send_message(
                    contact_id=viber_request.user.id,
                    message=f"{invitation}! 🙌\n\n"
                             "Якщо хочете дізнатись чи є світло саме зараз, натисніть кнопку 'Світло є?'\n\n"
                             "Якщо хочете отримувати повідомлення про світло, натисніть кнопку 'Підписатись'.",
                    keyboard=KBRD_SUBSCRIBE
                )
                Contact.create(
                    id=viber_request.user.id,
                    name=viber_request.user.name,
                    active=False,
                    last_access=datetime.utcnow()
                )
        elif isinstance(viber_request, ViberFailedRequest):
            logger.warning("Client failed to receive message. Failure: {0}".format(viber_request))

    except Exception as e:
        logger.error(f'GENERAL ERROR: {e}')
        logger.error(traceback.format_exc())

    return Response(status=200)


@inject
def _handle_message(
        viber_request,
        contact: Contact,
        contact_service: ContactService = Provide[Container.contact_service],
        messenger_bot: MessengerBot = Provide[Container.messenger_bot]
) -> None:

    message = viber_request.message
    logger.info(f"MESSAGE: {message.text}, CONTACT: {contact.id}")
    # contact_service = ViberContactService()
    keyboard = contact_service.get_keyboard(contact)

    if message.text == MSG_QUESTION_TEXT:
        messenger_bot.send_message(
            contact_id=viber_request.sender.id,
            message=pinger.get_current_state_info(),
            keyboard=keyboard
        )
        contact_service.touch(contact)

    elif message.text == MSG_SUBSCRIBE_TEXT:
        contact_service.subscribe(contact)
        keyboard = contact_service.get_keyboard(contact)
        messenger_bot.send_message(
            contact_id=viber_request.sender.id,
            message='Підписано на розсилку',
            keyboard=keyboard
        )

    elif message.text == MSG_UNSUBSCRIBE_TEXT:
        contact_service.unsubscribe(contact)
        keyboard = contact_service.get_keyboard(contact)
        messenger_bot.send_message(
            contact_id=viber_request.sender.id,
            message='Відписано від розсилки',
            keyboard=keyboard
        )

    elif message.text == MSG_ADMIN_STATS_TEXT:
        contacts = Contact.filter(Contact.active == True).order_by(Contact.last_access.desc()).objects()
        for c in contacts:
            message = f'```{c.formatted_info()}```'
            messenger_bot.send_message(
                contact_id=viber_request.sender.id,
                message=message,
                keyboard=keyboard
            )

    elif message.text in (MSG_ADMIN_MASK_TEXT, MSG_ADMIN_UNMASK_TEXT):
        pinger.masked = not pinger.masked
        keyboard = contact_service.get_keyboard(contact)  # FIXME: indirect dependency from pinger
        messenger_bot.send_message(
            contact_id=viber_request.sender.id,
            message=f'Розсилка повідомлень: {"ВИМКНЕНО" if pinger.masked else "УВІМКНЕНО"}!',
            keyboard=keyboard
        )

    elif message.text in (MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT, MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT):
        logger.info(f"Enabling forced state: {pinger.forced_state}")
        pinger.forced_state = message.text == MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
        keyboard = contact_service.get_keyboard(contact)  # FIXME: indirect dependency from pinger
        forced_state_str = "DISABLED" if pinger.forced_state is None else str(pinger.forced_state).upper()
        messenger_bot.send_message(
            contact_id=viber_request.sender.id,
            message=f'Forced state: {forced_state_str}',
            keyboard=keyboard
        )

    elif message.text in (MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT, MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT):
        logger.info(f"Disabling forced state: {pinger.forced_state}")
        pinger.forced_state = None
        forced_state_str = "DISABLED" if pinger.forced_state is None else str(pinger.forced_state).upper()
        keyboard = contact_service.get_keyboard(contact)  # FIXME: indirect dependency from pinger
        messenger_bot.send_message(
            contact_id=viber_request.sender.id,
            message=f'Forced state: {forced_state_str}',
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
