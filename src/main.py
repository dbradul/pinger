import os
import time
from threading import Thread

import requests

from web import create_app
from common.logger import logger
from app.containers import Container


FLASK_PORT = os.getenv('FLASK_PORT')
FLASK_DEBUG = bool(os.getenv('FLASK_DEBUG'))
BACKEND_STARTUP_DELAY = float(os.getenv('BACKEND_STARTUP_DELAY'))


def post_start():
    logger.debug("Post start")
    time.sleep(BACKEND_STARTUP_DELAY)
    requests.get(f'http://localhost:{FLASK_PORT}/register')
    requests.get(f'http://localhost:{FLASK_PORT}/init_db')


if __name__ == "__main__":
    Thread(target=post_start, daemon=True).start()

    container = Container()
    container.init_resources()
    container.wire(modules=[
        'common.handlers'
    ])

    pinger = container.pinger()
    pinger_listener = container.pinger_listener()
    pinger.add_listener(pinger_listener)
    pinger.start()

    app = create_app()
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
