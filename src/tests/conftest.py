import pytest
from peewee import SqliteDatabase, fn

from app.containers import Container
from common.models import Contact, History
from web import create_app

@pytest.fixture()
def app():
    container = Container()
    app = create_app(container)

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


# @pytest.fixture(scope='session', autouse=True)
@pytest.fixture(autouse=True)
def test_db(app):
    MODELS = [Contact, History]
    test_db = SqliteDatabase(':memory:')
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)
    yield test_db
    test_db.drop_tables(MODELS)
    test_db.close()


@pytest.fixture()
def random_user() -> Contact:
    return (
        Contact
        .select()
        .order_by(fn.Random())
        .limit(1)
        .get()
    )
