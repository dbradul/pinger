from concurrent.futures import ThreadPoolExecutor

import pytest
from peewee import fn
from unittest.mock import Mock

from common.models import Contact
from services import ContactService, MessengerBot


@pytest.fixture()
def messenger_bot(app) -> MessengerBot:
    return app.container.messenger_bot()

