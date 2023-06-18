from dataclasses import dataclass, asdict, field

from sqlalchemy import select, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.authentication import AuthenticationBackend, AuthCredentials, BaseUser, UnauthenticatedUser, requires
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from common.models import User, user_rights, Right
from common.repository import tables
from common.repository.users import create_db_user
from website.utils import JsonParams


class Table(HTTPEndpoint):
    """ Обработка запросов на получение таблиц
    """

    async def get(self, request: Request):
        engine = request.app.state.postgres  # type: AsyncEngine
        if request.user.is_authenticated:
            username = request.session['user']['display_name']
            async with engine.connect() as conn:
                return JSONResponse(
                    await tables.get_users_table(conn=conn, current_user=username))
        else:
            raise HTTPException(401)

    async def post(self, request: Request):
        engine = request.app.state.postgres
        async with JsonParams(request) as param:
            filename = param.get('filename')
            user = request.session['user']['display_name']
            async with engine.connect() as conn:
                password = await (await conn.stream(
                    text("""select password from users where username = '{}'""".format(user)))).first()

        import subprocess
        # Скрипт загрузки файла в бд
        command = """cd ~/Рабочий\ стол/shapes/ && shp2pgsql {} | PGPASSWORD='{}' psql -p 54320 -h localhost -d geodb -U {}""".format(
            filename[:-4], password[0], user)
        subprocess.run(command, shell=True)
        return JSONResponse('ok')


routes = [
    Route('/singtable', endpoint=Table),
]
