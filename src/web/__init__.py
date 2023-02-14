import logging

from flask import Flask

from .router import router


def create_app(container):

    app = Flask(__name__)
    # app.config.from_object('src.config.Config')
    app.logger.setLevel(logging.INFO)
    app.container = container

    # register routes
    for route in router.routes:
        app.add_url_rule(
            rule=route.url,
            view_func=route.view_func,
            methods=route.methods
        )

    return app
