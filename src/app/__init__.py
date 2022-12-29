from flask import Flask

from app import routes


def create_app():
    app = Flask(__name__)
    # app.config.from_object('src.config.Config')

    # import routes
    for url in routes.ROUTES:
        app.add_url_rule(url, view_func=routes.ROUTES[url])

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