import os
import requests
import time
from threading import Thread

from app import create_app
from common.logger import logger
from common.pinger import Pinger
from viber.bot import ViberBot


FLASK_PORT = os.getenv('FLASK_PORT')
FLASK_DEBUG = bool(os.getenv('FLASK_DEBUG'))
BACKEND_STARTUP_DELAY = float(os.getenv('BACKEND_STARTUP_DELAY'))


def post_start():
    logger.debug("Post start")
    time.sleep(BACKEND_STARTUP_DELAY)
    requests.get(f'http://localhost:{FLASK_PORT}/register')
    requests.get(f'http://localhost:{FLASK_PORT}/init_db')


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    Thread(target=post_start, daemon=True).start()

    viber_bot = ViberBot()

    pinger = Pinger()
    pinger.add_listeners(
        viber_bot.dump_event,
        viber_bot.notify_subscribers
    )
    pinger.start()

    app = create_app()
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
