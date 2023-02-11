from typing import Callable, List

from dataclasses import dataclass

from web import views


@dataclass
class Route:
    url: str
    view_func: Callable
    methods: List[str]


@dataclass
class Router:
    routes: List[Route]


router = Router(
    routes=[
        Route('/register', views.register, methods=['GET']),
        Route('/init_db', views.init_db, methods=['GET']),
        Route('/', views.webhook, methods=['POST'])
    ]
)