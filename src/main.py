import os
import time
from threading import Thread

import requests

from web import create_app
from common.logger import logger
from app.containers import Container


FLASK_PORT = os.getenv('FLASK_PORT')
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
    # container.wire(modules=[
    #     # 'services.message_handlers',
    #     'web.views',
    # ])

    pinger = container.pinger()
    pinger_listener = container.pinger_listener()
    pinger.add_listener(pinger_listener)
    pinger.start()

    logger.info('Configuring Flask app...')
    app = create_app()
    logger.info('Running Flask app...')
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
