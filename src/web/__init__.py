import logging

from flask import Flask

from . import router
from . import views
# from .router import Route, Router
from .router import router


def create_app():
    # from web import router

    app = Flask(__name__)
    # app.config.from_object('src.config.Config')
    app.logger.setLevel(logging.INFO)

    # import routes
    # for url in routes.ROUTES:
    #     view_func, methods = routes.ROUTES[url]
    #     app.add_url_rule(url, view_func=view_func, methods=methods)

    # register views

    # router = Router(
    #     routes=[
    #         Route('/register', views.register, methods=['GET']),
    #         Route('/init_db', views.init_db, methods=['GET']),
    #         Route('/', views.webhook, methods=['POST'])
    #     ]
    # )

    # register routes
    for route in router.routes:
        app.add_url_rule(
            rule=route.url,
            view_func=route.view_func,
            methods=route.methods
        )

    return app



# app = Flask(__name__)
# # app.config.from_object('src.config.Config')
#
# # import routes
# for url in routes.ROUTES:
#     app.add_url_rule(url, view_func=routes.ROUTES[url])

# app = Flask(__name__)

# from app import routes
#
#
# app.run(debug=True)