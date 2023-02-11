import viberbot
import telegram

import bot.resources
import common
import services

from dependency_injector import containers, providers

import web
# from web.handlers import register, init_db


class Container(containers.DeclarativeContainer):
    # config = providers.Configuration(ini_files=["config.ini"])
    #
    # logging = providers.Resource(
    #     logging.config.fileConfig,
    #     fname="logging.ini",
    # )


    # Config
    config = providers.Configuration()
    config.ROUTER_IP.from_env("ROUTER_IP")
    config.ROUTER_PORT.from_env("ROUTER_PORT")
    config.ROUTER_USER.from_env("ROUTER_USER")
    config.ROUTER_PASSWORD.from_env("ROUTER_PASSWORD")
    config.ROUTER_REQUEST_TIMEOUT.from_env("ROUTER_REQUEST_TIMEOUT")

    config.BOT_BACKEND.from_env("BOT_BACKEND")
    config.VIBER_API_TOKEN.from_env("VIBER_API_TOKEN")
    config.VIBER_ADMIN_IDS.from_env("VIBER_ADMIN_IDS")
    config.TELEGRAM_API_TOKEN.from_env("TELEGRAM_API_TOKEN")
    config.TELEGRAM_ADMIN_IDS.from_env("TELEGRAM_ADMIN_IDS")

    config.OUTLIERS_FILEPATH.from_env("OUTLIERS_FILEPATH")
    config.RATE_LIMIT_CALL_NUM.from_env("RATE_LIMIT_CALL_NUM")
    config.RATE_LIMIT_PERIOD_SEC.from_env("RATE_LIMIT_PERIOD_SEC")

    # Bot
    viber_bot_api_configuration = providers.Singleton(
        viberbot.BotConfiguration,
        name='Світло 4, 10',
        avatar='http://site.com/avatar.jpg',
        auth_token=config.VIBER_API_TOKEN()
    )

    viber_bot_api = providers.Singleton(
        viberbot.Api,
        bot_configuration=viber_bot_api_configuration,
    )

    tg_bot_api = providers.Singleton(
        telegram.Bot,
        token=config.TELEGRAM_API_TOKEN()
    )

    viber_resource = providers.Factory(
        bot.resources.ViberResource
    )

    tg_resource = providers.Factory(
        bot.resources.TelegramResource
    )


    # Services
    messenger_bot = providers.Selector(
        config.BOT_BACKEND,
        viber=providers.Singleton(
            services.ViberMessengerBot,
            api_client=viber_bot_api,
            resource=viber_resource,
            admin_ids=config.VIBER_ADMIN_IDS
        ),
        telegram=providers.Singleton(
            services.TelegramMessengerBot,
            api_client=tg_bot_api,
            resource=tg_resource,
            admin_ids=config.TELEGRAM_ADMIN_IDS
        ),
    )

    contact_service = providers.Factory(
        services.ContactService,
        messenger_bot=messenger_bot,
    )

    history_service = providers.Factory(
        services.HistoryService
    )


    # Pinger
    ssh_remote_host = providers.Factory(
        common.remote_host.SSHRemoteHost,
        host=config.ROUTER_IP(),
        port=config.ROUTER_PORT.as_int(),
        user=config.ROUTER_USER(),
        password=config.ROUTER_PASSWORD(),
        timeout=config.ROUTER_REQUEST_TIMEOUT.as_float()
    )

    pinger = providers.Singleton(
        services.Pinger,
        daemon=True,
        remote_host=ssh_remote_host
    )

    pinger_listener = providers.Factory(
        services.PingerListener,
        contact_service=contact_service,
        history_service=history_service,
        messenger_bot=messenger_bot,
        failed_contacts_filepath=config.OUTLIERS_FILEPATH()
    )

    # Web
    wiring_config = containers.WiringConfiguration(
        modules=[
            "web.views"
        ],
    )

    message_handler = providers.Selector(
        config.BOT_BACKEND,
        viber=providers.Factory(
            services.ViberMessageHandler,
            messenger_bot=messenger_bot,
            contact_service=contact_service,
            pinger=pinger,
            outliers_filepath=config.OUTLIERS_FILEPATH(),
            rate_limit_call_num=config.RATE_LIMIT_CALL_NUM.as_int(),
            rate_limit_period_sec=config.RATE_LIMIT_PERIOD_SEC.as_int()
        ),
        telegram=providers.Factory(
            services.TelegramMessageHandler,
            messenger_bot=messenger_bot,
            contact_service=contact_service,
            pinger=pinger,
            outliers_filepath=config.OUTLIERS_FILEPATH(),
            rate_limit_call_num=config.RATE_LIMIT_CALL_NUM.as_int(),
            rate_limit_period_sec=config.RATE_LIMIT_PERIOD_SEC.as_int()
        ),
    )

    # routes = providers.List(
    #     providers.Factory(
    #         web.router.Route,
    #         url='/incoming',
    #         view_func=incoming_webhook.provider,
    #         methods=['POST']
    #     ),
    #     providers.Factory(
    #         web.router.Route,
    #         url='/register',
    #         view_func=providers.Callable(
    #             web.views.register,
    #             messenger_bot=messenger_bot
    #         ).provider,
    #         methods=['GET']
    #     ),
    #     providers.Factory(
    #         web.router.Route,
    #         url='/init_db',
    #         view_func=providers.Callable(
    #             web.views.init_db,
    #             messenger_bot=messenger_bot
    #         ).provider,
    #         methods=['GET']
    #     )
    # )
    #
    # # routes = [
    # #     web.router.Route(
    # #         url='/incoming',
    # #         view_func=incoming_webhook.provider,
    # #         methods=['POST']
    # #     )
    # # ]
    #
    # router = providers.Factory(
    #     web.router.Router,
    #     routes=routes
    # )
