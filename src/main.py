import os

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
import logging

from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

from webargs import fields
from webargs.flaskparser import use_kwargs

from src.keyboards import KBRD_CHECK_LIGHT, MSG_QUESTION_TEXT

PORT=os.getenv('PORT')
API_TOKEN=os.getenv('API_TOKEN')
ROUTER_IP = '213.231.6.236'

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='gem4',
    avatar='http://site.com/avatar.jpg',
    auth_token=API_TOKEN
))
# logger = logging.getLogger(__name__ )
logger = app.logger

def is_online(ip_address):
    response = os.system("ping -c 1 " + ip_address)
    return response == 0

# @app.route('/', methods=['POST'])
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

            app.logger.info(f"MESSAGE: {message.text}")
            if message.text == MSG_QUESTION_TEXT or True:

                info = 'Світло є!' if is_online(ROUTER_IP) else 'Світла немає ;('
                # message = TextMessage(
                #     text=info,
                #     keyboard=CHECK_LIGHT
                # )
                message_info = TextMessage(
                    text=info,
                    keyboard=KBRD_CHECK_LIGHT
                )
                # message_kbrd = KeyboardMessage(
                #     keyboard=CHECK_LIGHT,
                #     min_api_version=3
                # )

                viber.send_messages(viber_request.sender.id, [
                    message_info,
                    # message_kbrd
                ])
        elif isinstance(viber_request, ViberSubscribedRequest):
            viber.send_messages(viber_request.get_user.id, [
                TextMessage(text="thanks for subscribing!")
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


if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    # app.run(host='0.0.0.0', port=443, debug=True, ssl_context=context)
    app.run(host='0.0.0.0', port=PORT, debug=True)

