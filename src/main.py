from web import create_app
from common.logger import logger
from app.containers import Container


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.init_thread().start()

    pinger = container.pinger()
    pinger_listener = container.pinger_listener()
    pinger.add_listener(pinger_listener)
    pinger.start()

    logger.info('Configuring Flask app...')
    app = create_app(container)
    logger.info('Running Flask app...')
    app.run(host='0.0.0.0', port=container.config.FLASK_PORT(), debug=False)
