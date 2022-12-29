import os

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration


VIBER_API_TOKEN = os.getenv('VIBER_API_TOKEN')

viber = Api(BotConfiguration(
    name='gem4',
    avatar='http://site.com/avatar.jpg',
    auth_token=VIBER_API_TOKEN
))