from common.handlers import incoming, register, init_db

ROUTES = {
    '/': incoming,
    '/register': register,
    '/init_db': init_db,
}