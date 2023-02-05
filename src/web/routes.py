import os

from web.handlers import incoming, incoming_tg, register, init_db
# from web.views import BaseView

ROUTES = {
    # '/': (incoming, ['POST']),
    '/': (incoming if os.getenv('BOT_BACKEND') == 'viber' else incoming_tg, ['POST']),
    '/register': (register, ['GET']),
    '/init_db': (init_db, ['GET'])
}