import pytest

from bot import MessengerBot


@pytest.fixture()
def messenger_bot(app) -> MessengerBot:
    return app.container.messenger_bot()

