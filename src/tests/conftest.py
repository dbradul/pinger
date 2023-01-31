import pytest
from src.web import create_app
# from app import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here
    # from src.common.models import db

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()
