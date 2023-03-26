from sqlalchemy.ext.asyncio import create_async_engine
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from test import test

from common.envars import DATABASE_URL


class Application(Starlette):
    """ Web application
    """

    def __init__(self):
        Starlette.__init__(self, routes=[
            Mount('/api', routes=[
                Route('/test', test, methods=["POST", "GET"]),
            ], )
        ])
        self.state.postgres = create_async_engine(DATABASE_URL)

