import os
from datetime import datetime
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from webargs import fields
from webargs.flaskparser import use_kwargs

from src.keyboards import *
from src.models import Contact

PORT = os.getenv('PORT')
API_TOKEN = os.getenv('API_TOKEN')
ROUTER_IP = os.getenv('ROUTER_IP')


# app = Flask(__name__)
viber = Api(BotConfiguration(
    name='gem4',
    avatar='http://site.com/avatar.jpg',
    auth_token=API_TOKEN
))

from app import app
# logger = logging.getLogger(__name__ )
logger = app.logger


def is_online(ip_address):
    response = os.system("ping -c 1 " + ip_address)
    return response == 0


@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))

    try:
        # every viber message is signed, you can verify the signature using this method
        if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
            return Response(status=403)

        # this library supplies a simple way to receive a request object
        viber_request = viber.parse_request(request.get_data())

        if isinstance(viber_request, ViberMessageRequest):
            message = viber_request.message
            contact = Contact.get_or_none(Contact.id == viber_request.sender.id)
            DEFAULT_KEYBOARD = KBRD_UNSUBSCRIBE if (contact and contact.active) else KBRD_SUBSCRIBE

            app.logger.info(f"MESSAGE: {message.text}")
            if message.text == MSG_QUESTION_TEXT:

                info = 'Світло є!' if is_online(ROUTER_IP) else 'Світла немає ;('

                # message_kbrd = KeyboardMessage(
                #     keyboard=CHECK_LIGHT,
                #     min_api_version=3
                # )

                viber.send_messages(viber_request.sender.id, [
                    TextMessage(
                        text=info,
                        keyboard=DEFAULT_KEYBOARD
                    )
                ])
            elif message.text == MSG_SUBSCRIBE_TEXT:
                # contact = Contact.get_or_none(Contact.id == viber_request.sender.id)
                if contact is None:
                    Contact.create(
                        id=viber_request.sender.id,
                        name=viber_request.sender.name,
                        active=True,
                        last_access = datetime.utcnow()
                    )
                else:
                    contact.active = True
                    contact.last_access = datetime.utcnow()
                    contact.save()

                viber.send_messages(viber_request.sender.id, [
                    TextMessage(
                        text='Підписано на розсилку',
                        keyboard=KBRD_UNSUBSCRIBE
                    )
                ])

            elif message.text == MSG_UNSUBSCRIBE_TEXT:
                # contact = Contact.get_or_none(Contact.id == viber_request.sender.id)
                if contact is not None:
                    contact.active = False
                    contact.last_access = datetime.utcnow()
                    contact.save()
                else:
                    app.logger.error(f"Contact {viber_request.sender.id} not found, but is trying to unsubscribe!")

                viber.send_messages(viber_request.sender.id, [
                    TextMessage(
                        text='Відписано від розсилки',
                        keyboard=KBRD_SUBSCRIBE
                    )
                ])

        elif isinstance(viber_request, ViberSubscribedRequest):
            viber.send_messages(viber_request.get_user.id, [
                TextMessage(text="thanks for subscribing!")
            ])
        elif isinstance(viber_request, ViberConversationStartedRequest):
            viber.send_messages(viber_request.user.id, [
                TextMessage(
                    text=f"""Вітаю, {viber_request.user.name}! 🙌
                    
                    Якщо ти хочеш отримувати повідомлення про світло, натисни кнопку 'Підписатись'.
                    Якщо хочеш дізнатись чи є світло саме зараз, натисни кнопку 'Світло є?'
                    """,
                    keyboard=KBRD_SUBSCRIBE
                )
            ])
        elif isinstance(viber_request, ViberFailedRequest):
            logger.warn("client failed receiving message. failure: {0}".format(viber_request))
    except Exception as e:
        logger.error(e)

    return Response(status=200)


@app.route('/register', methods=['GET'])
@use_kwargs(
    {
        "url": fields.Str()
    },
    location="query",
)
def register(url):
    logger.debug("received request. post data: {0}".format(request.get_data()))

    viber.set_webhook(url)

    return 'OK - Registered'


@app.route('/init_db', methods=['GET'])
def init_db():
    logger.debug("received request. get data: {0}".format(request.get_data()))

    Contact.create_table()

    return 'OK - Created'

if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    # app.run(host='0.0.0.0', port=443, debug=True, ssl_context=context)
    app.run(host='0.0.0.0', port=PORT, debug=True)

