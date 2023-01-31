from common.handlers import incoming, register, init_db

ROUTES = {
    '/': (incoming, ['POST']),
    '/register': (register, ['GET']),
    '/init_db': (init_db, ['GET']),
}