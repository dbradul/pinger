import copy
import logging
import os
import re
import sys
import traceback

import requests
import time
from datetime import datetime, timedelta
from flask import request, Response
from threading import Thread
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest, ViberUnsubscribedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest

from app import app
from helpers import ScopeRateLimiter
from keyboards import *
from models import Contact, History

# logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler())
log_file = './logs/bot.log'
logger = app.logger
# logger.addHandler(logging.StreamHandler())StreamHandler
logging.basicConfig(level=logging.INFO, filename=log_file,
                    format="%(asctime)-15s %(threadName)s %(levelname)-8s %(message)s")


PORT = os.getenv('PORT')
API_TOKEN = os.getenv('API_TOKEN')
ROUTER_IP = os.getenv('ROUTER_IP')
ROUTER_PORT = os.getenv('ROUTER_PORT')
ROUTER_REQUEST_TIMEOUT = float(os.getenv('ROUTER_REQUEST_TIMEOUT'))
ROUTER_REQUEST_INTERVAL = float(os.getenv('ROUTER_REQUEST_INTERVAL'))
PROBE_COUNT_LIMIT = float(os.getenv('PROBE_COUNT_LIMIT'))
BACKEND_STARTUP_DELAY = float(os.getenv('BACKEND_STARTUP_DELAY'))
LIGHT_ON = 'Світло є'
LIGHT_OFF = 'Світла немає'
BOT_TAG = '📢'
ADMIN_IDS = os.getenv('ADMIN_IDS').split(',')


rate_limiter = ScopeRateLimiter(calls=5, period=10)

viber = Api(BotConfiguration(
    name='gem4',
    avatar='http://site.com/avatar.jpg',
    auth_token=API_TOKEN
))

g_current_state = None
g_is_masked = False


def get_current_state_info(current_state, bot=False):
    tag = BOT_TAG if bot else ""
    state_info = LIGHT_ON if current_state else LIGHT_OFF
    return f'{tag} {state_info}'


def get_contact_keyboard(contact):
    keyboard = KBRD_UNSUBSCRIBE if (contact and contact.active) else KBRD_SUBSCRIBE
    if contact and contact.id in ADMIN_IDS:
        keyboard = copy.deepcopy(keyboard)
        keyboard['Buttons'].extend(get_admin_keyboard(g_is_masked))
    return keyboard


def is_online(ip_address, port):
    app.logger.info(f"REQUESTING {ip_address}...")
    # response = os.system(f"ping -c 1 -W {PING_TIMEOUT} {ip_address}")
    # return response == 0
    try:
        response = requests.get(f"http://{ip_address}:{port}", timeout=ROUTER_REQUEST_TIMEOUT)
        result = response.status_code == 200
    except requests.exceptions.ConnectTimeout as ex:
        app.logger.error(f"ROUTER REQUEST TIMEOUT: {ex}")
        result = False
    except Exception as ex:
        app.logger.error(f"ROUTER GENERAL ERROR: {ex}")
        result = False
    return result


def post_start():
    logger.debug("Post start")
    time.sleep(BACKEND_STARTUP_DELAY)
    requests.get(f'http://localhost:{PORT}/register')
    requests.get(f'http://localhost:{PORT}/init_db')


@app.route('/', methods=['POST'])
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
            keyboard = get_contact_keyboard(contact)

            if contact is None:
                app.logger.error(f"Contact {viber_request.sender.id} not found in DB!")
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(
                        text='Ваш контакт не знайдено. Спробуйте додатись до чату знову.',
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
                handle_message(viber_request, contact, keyboard)

        elif isinstance(viber_request, ViberUnsubscribedRequest):
            contact = Contact.get_or_none(Contact.id == viber_request.user_id)
            if contact:
                contact.delete_instance()

        elif isinstance(viber_request, ViberConversationStartedRequest):
            contact = Contact.get_or_none(Contact.id == viber_request.user.id)
            if contact is None:
                viber.send_messages(viber_request.user.id, [
                    TextMessage(
                        text=f"Вітаю, {viber_request.user.name}! 🙌\n\n"
                             "Якщо хочете отримувати повідомлення про світло, натисніть кнопку 'Підписатись'.\n"
                             "Якщо хочете дізнатись чи є світло саме зараз, натисніть кнопку 'Світло є?'",
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


def handle_message(viber_request, contact, keyboard):
    global g_is_masked
    message = viber_request.message
    app.logger.info(f"MESSAGE: {message.text}")

    if message.text == MSG_QUESTION_TEXT:
        info = get_current_state_info(g_current_state)
        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                text=info,
                keyboard=keyboard
            )
        ])
        contact.count_requests += 1
        contact.save()
    elif message.text == MSG_SUBSCRIBE_TEXT:
        contact.active = True
        contact.last_access = datetime.utcnow()
        contact.save()
        keyboard = get_contact_keyboard(contact)

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
        keyboard = get_contact_keyboard(contact)

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
        g_is_masked = not g_is_masked
        keyboard = get_contact_keyboard(contact)
        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                text=f'Розсилка повідомлень: {"ВИМКНЕНО" if g_is_masked else "УВІМКНЕНО"}!',
                keyboard=keyboard
            )
        ])
    return True


@app.route('/register', methods=['GET'])
def register():
    logger.debug("Registering")

    log_path = '/app/logs/ngrok.log'
    with open(log_path) as f:
        # content = f.read()
        for line in f.readlines():
            m = re.match('.*msg="started tunnel" .*url=https://(.*)$', line)
            if m:
                ngrok_url = m.groups(0)[0]
                viber.set_webhook('https://' + ngrok_url)
                logger.info(f"SELF REGISTERING DONE: {ngrok_url}")
                break
        else:
            app.logger.error('URL IS NOT RECOGNIZED')

    return 'OK - Registered'


@app.route('/init_db', methods=['GET'])
def init_db():
    logger.debug("received request. get data: {0}".format(request.get_data()))
    Contact.create_table()
    return 'OK - Created'


def dump_event(current_state):
    event = get_current_state_info(current_state)
    History.create(event_date=datetime.utcnow(), event_type=event)


def notify_subscribers(current_state):
    look_back_window = datetime.utcnow() - timedelta(minutes=0)
    contacts = Contact.filter(Contact.active == True, Contact.last_access <= look_back_window).objects()
    logger.info(f"SUBSCRIBERS TO NOTIFY: {contacts.count()}")
    # for i in range(100):
    for contact in contacts:
        try:
            logger.info(f"  SENDING NOTIFICATION TO CONTACT: {contact.name}, {contact.id}")
            keyboard = get_contact_keyboard(contact)
            viber.send_messages(contact.id, [
                TextMessage(
                    # text=get_current_state_info(current_state, bot=True) + f" ({i})",
                    text=get_current_state_info(current_state, bot=True),
                    keyboard=keyboard
                )
            ])
            contact.last_access = datetime.utcnow()
            contact.save()
        except Exception as e:
            logger.error(f"ERROR SENDING MESSAGE TO {contact.id}: {e}")
            logger.error(traceback.format_exc())


def ping():
    global g_current_state
    current_state = None
    probe_count = 0
    while True:
        try:
            result = is_online(ROUTER_IP, ROUTER_PORT)
            if current_state is None:
                current_state = result
                g_current_state = current_state
            else:
                if result != current_state:
                    probe_count += 1
                else:
                    probe_count = 0

                if probe_count == PROBE_COUNT_LIMIT:
                    probe_count = 0
                    current_state = result
                    g_current_state = current_state
                    if not g_is_masked:
                        logger.info('STATE HAS CHANGED! NOTIFYING SUBSCRIBERS!')
                        dump_event(current_state)
                        notify_subscribers(current_state)
                    else:
                        logger.info('STATE HAS CHANGED! NOTIFICATIONS ARE DISABLED!')

            logger.info('CURRENT STATE (ONLINE): %s', current_state)
            logger.info('PING_INTERVAL: %s', ROUTER_REQUEST_INTERVAL)
            time.sleep(ROUTER_REQUEST_INTERVAL)

        except Exception as e:
            logger.error(f'GENERAL ERROR: {e}')
            logger.error(traceback.format_exc())
            #sys.exit(1)


if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    # app.run(host='0.0.0.0', port=443, debug=True, ssl_context=context)
    Thread(target=post_start, daemon=True).start()
    Thread(target=ping, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT, debug=False)
