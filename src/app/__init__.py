import logging

from flask import Flask




def create_app():
    from app import routes

    app = Flask(__name__)
    # app.config.from_object('src.config.Config')
    app.logger.setLevel(logging.INFO)

    # import routes
    for url in routes.ROUTES:
        view_func, methods = routes.ROUTES[url]
        app.add_url_rule(url, view_func=view_func, methods=methods)

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