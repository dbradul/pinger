import os

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
import logging

from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

PORT=os.getenv('PORT')
API_TOKEN=os.getenv('API_TOKEN')

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='gem4',
    avatar='http://site.com/avatar.jpg',
    auth_token=API_TOKEN
))
logger = logging.getLogger(__name__ )


# @app.route('/', methods=['POST'])
@app.route('/', methods=['POST', 'GET'])
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
            # lets echo back
            viber.send_messages(viber_request.sender.id, [
                message
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

if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    # app.run(host='0.0.0.0', port=443, debug=True, ssl_context=context)
    app.run(host='0.0.0.0', port=PORT, debug=True)

