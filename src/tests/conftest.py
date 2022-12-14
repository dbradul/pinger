import pytest
from src.app import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here
    from src.pinger.models import db

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()
