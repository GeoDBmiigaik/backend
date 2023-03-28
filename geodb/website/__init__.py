from sqlalchemy.ext.asyncio import create_async_engine
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from common.envars import DATABASE_URL, COOKIE_SECRET_KEY
from website import users
from common.envars import DATABASE_URL


class Application(Starlette):
    """ Web application
    """

    def __init__(self):
        Starlette.__init__(self, routes=[
            Mount('/api', routes=[
                Mount('/users', routes=users.routes),
            ], )
        ], middleware=[
            Middleware(CORSMiddleware, allow_origins=['*']),
            Middleware(SessionMiddleware, secret_key=COOKIE_SECRET_KEY),
            Middleware(AuthenticationMiddleware, backend=users.AuthBackend()),
        ])
        self.state.postgres = create_async_engine(DATABASE_URL)

