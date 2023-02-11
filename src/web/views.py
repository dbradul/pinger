import re
import traceback

from dependency_injector.wiring import Provide, inject
from flask import request, Response

from app.containers import Container
from common.logger import logger
from common.models import Contact, History
from services import MessengerBot
from services.message_handlers import MessageHandler


@inject
def webhook(message_handler: MessageHandler = Provide[Container.message_handler]):
    logger.debug("received request. post data: {0}".format(request.get_data()))

    if not message_handler.handle_incoming(request.get_data(), request.headers):
        return Response(status=403)

    return Response(status=200)


@inject
def register(messenger_bot: MessengerBot = Provide[Container.messenger_bot]):
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


def init_db():
    logger.debug("received request. get data: {0}".format(request.get_data()))
    Contact.create_table()
    History.create_table()
    return 'OK - Created'

