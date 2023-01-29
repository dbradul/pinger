import os
import requests
import time
from threading import Thread

from viberbot import Api, BotConfiguration

from app import create_app
from services.bot import ViberMessengerBot
from common.logger import logger
from common.pinger import Pinger
from pinger.containers import Container
from services.messengers import MessengerService
# from viber.bot import ViberBot


FLASK_PORT = os.getenv('FLASK_PORT')
FLASK_DEBUG = bool(os.getenv('FLASK_DEBUG'))
BACKEND_STARTUP_DELAY = float(os.getenv('BACKEND_STARTUP_DELAY'))
VIBER_API_TOKEN = os.getenv('VIBER_API_TOKEN')


def post_start():
    logger.debug("Post start")
    time.sleep(BACKEND_STARTUP_DELAY)
    requests.get(f'http://localhost:{FLASK_PORT}/register')
    requests.get(f'http://localhost:{FLASK_PORT}/init_db')


if __name__ == "__main__":
    Thread(target=post_start, daemon=True).start()

    container = Container()
    container.init_resources()
    container.wire(modules=['common.handlers'])

    # viber_bot = ViberBot()

    # viber_backend = ViberBotBackend(
    #     api_client=Api(BotConfiguration(
    #         name='Світло 4-10',
    #         avatar='http://site.com/avatar.jpg',
    #         auth_token=VIBER_API_TOKEN
    #     )))

    messenger = MessengerService(
        # backend=viber_backend
    )

    pinger = Pinger()
    pinger.add_listener(
        # viber_bot.dump_event,
        # viber_bot.notify_subscribers
        messenger.on_state_change
    )
    pinger.start()

    app = create_app()
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
