from flask import Flask

def create_app():
    app = Flask(__name__)
    # app.config.from_object('src.config.Config')
    return app


# app = Flask(__name__)

# from app import routes
#
#
# app.run(debug=True)