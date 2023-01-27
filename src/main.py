import copy
import datetime
import logging
import os
import paramiko
import re
import requests
import time
import traceback
from datetime import datetime, timedelta
from flask import request, Response, render_template
from threading import Thread
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest, ViberUnsubscribedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest

from app import create_app
from pinger.helpers import ScopeRateLimiter
from pinger.keyboards import *
from pinger.models import Contact, History

# logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler())
app = create_app()
log_file = './logs/bot.log'
logger = app.logger
# logger.addHandler(logging.StreamHandler())StreamHandler
logging.basicConfig(level=logging.INFO, filename=log_file,
                    format="%(asctime)-15s %(threadName)s %(levelname)-8s %(message)s")


FLASK_PORT = os.getenv('FLASK_PORT')
FLASK_DEBUG = bool(os.getenv('FLASK_DEBUG'))
VIBER_API_TOKEN = os.getenv('VIBER_API_TOKEN')
ROUTER_IP = os.getenv('ROUTER_IP')
ROUTER_USER = os.getenv('ROUTER_USER')
ROUTER_PASSWORD = os.getenv('ROUTER_PASSWORD')
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
    name='Світло 4-10',
    avatar='http://site.com/avatar.jpg',
    auth_token=VIBER_API_TOKEN
))

g_current_state = None
g_forced_state = None
g_is_masked = False


def get_current_state_info(current_state, bot=False):
    tag = BOT_TAG if bot else ""
    state_info = LIGHT_ON if current_state else LIGHT_OFF
    return f'{tag} {state_info}'


def get_contact_keyboard(contact):
    keyboard = KBRD_UNSUBSCRIBE if (contact and contact.active) else KBRD_SUBSCRIBE
    if contact and contact.id in ADMIN_IDS:
        keyboard = copy.deepcopy(keyboard)
        keyboard['Buttons'].extend(get_admin_keyboard(g_is_masked, g_forced_state))
    return keyboard


def is_online():
    app.logger.info(f"REQUESTING ROUTER {ROUTER_IP}...")

    if g_forced_state is not None:
        app.logger.info(f"Forced state is returned: {g_forced_state}")
        return g_forced_state

    result = False
    client = None

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=ROUTER_IP,
            username=ROUTER_USER,
            password=ROUTER_PASSWORD,
            port=ROUTER_PORT,
            timeout=ROUTER_REQUEST_TIMEOUT,
            allow_agent=False
        )
        result = True
    except Exception as ex:
        app.logger.error(f"ROUTER GENERAL ERROR: {ex}")
    finally:
        if client:
            client.close()

    return result


def post_start():
    logger.debug("Post start")
    time.sleep(BACKEND_STARTUP_DELAY)
    requests.get(f'http://localhost:{FLASK_PORT}/register')
    requests.get(f'http://localhost:{FLASK_PORT}/init_db')


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
                        text='Ваш контакт не знайдено. Спробуйте видалити чат та додатись до нього знову.',
                        # keyboard=keyboard
                    )
                ])
            elif not allowed:
                logger.error(f'RATE LIMIT IS EXCEEDED FOR USER: {viber_request.sender.id}')
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(
                        text='_Перевищено ліміт запитів. Спробуйте пізніше._',
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


def handle_message(viber_request, contact, keyboard):
    global g_is_masked
    global g_forced_state

    message = viber_request.message
    app.logger.info(f"MESSAGE: {message.text}, CONTACT: {contact.id}")

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

    elif message.text in (MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT, MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT):
        g_forced_state = True if message.text == MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT else False
        app.logger.info(f"Enabling forced state: {g_forced_state}")
        keyboard = get_contact_keyboard(contact)
        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                text=f'Forced state: {"DISABLED" if g_forced_state is None else ["FALSE", "TRUE"][g_forced_state]}',
                keyboard=keyboard
            )
        ])

    elif message.text in (MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT, MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT):
        g_forced_state = None
        app.logger.info(f"Disabling forced state: {g_forced_state}")
        keyboard = get_contact_keyboard(contact)
        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                text=f'Forced state: {"DISABLED" if g_forced_state is None else ["FALSE", "TRUE"][g_forced_state]}',
                keyboard=keyboard
            )
        ])

    elif message.text == MSG_ADMIN_FORCED_RESEND_TEXT:
        with open('./data/outliers.txt', 'r') as f:
            outliers = f.read().splitlines()
            for outlier in outliers:
                outlier = outlier.split(',')
                viber.send_messages(outlier[0], [
                    TextMessage(
                        text=outlier[1],
                        keyboard=keyboard
                    )
                ])
        app.logger.info(f"Disabling forced state: {g_forced_state}")
        keyboard = get_contact_keyboard(contact)
        viber.send_messages(viber_request.sender.id, [
            TextMessage(
                text=f'Forced state: {"DISABLED" if g_forced_state is None else ["FALSE", "TRUE"][g_forced_state]}',
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
    History.create_table()
    return 'OK - Created'

@app.route('/invitation', methods=['GET'])
def invitation():
    logger.debug("received request. get data: {0}".format(request.get_data()))
    return render_template('invitation.html')

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
            result = is_online()
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
    Thread(target=post_start, daemon=True).start()
    Thread(target=ping, daemon=True).start()
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
