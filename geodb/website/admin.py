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

from backend.geodb.common.repository.tables import get_users_tables_namelist


class Merging(HTTPEndpoint):
    """ Слияния баз данных
    """

    async def post(self, request: Request):
        engine = request.app.state.postgres
        async with JsonParams(request) as param:
            # Копирование ролей из одной бд в другую
            first_command = """PGPASSWORD={} pg_dumpall --globals-only -U {} -h {} -p {} |
            PGPASSWORD={} psql -h {} -p {} -U {}""".format(param['first_password'], param['first_username'],
                                                           param['first_host'], param['first_port'],
                                                           param['second_password'], param['second_host'],
                                                           param['second_port'], param['second_username'], )

            async with engine.connect() as conn:
                s = await get_users_tables_namelist(conn, param['first_username'])

            second_command = """PGPASSWORD={} pg_dump -U {} -h {} -p {} -d {}""".format(param['first_password'],
                                                                                        param['first_username'],
                                                                                        param['first_host'],
                                                                                        param['first_port'],
                                                                                        param['first_db_name']) + s \
                             + """ | PGPASSWORD={} psql -h {} -p {} -U {} -d {}""".format(param['second_password'],
                                                                                          param['second_host'],
                                                                                          param['second_port'],
                                                                                          param['second_username'],
                                                                                          param['second_db_name'])

        import subprocess

        subprocess.run(first_command, shell=True)
        subprocess.run(second_command, shell=True)

        return JSONResponse('ok')


class Roler(HTTPEndpoint):

    async def get(self, request: Request):
        engine = request.app.state.postgres
        resp = {'roles': [], 'tables': []}
        async with engine.connect() as conn:
            roles = await conn.stream(
                text("""SELECT usename AS role_name
                        FROM pg_catalog.pg_user"""))
            print(roles)
            async for row in roles:
                resp['roles'].append(row[0])
            tables = await conn.stream(
                text("""SELECT table_name
                        FROM information_schema.tables
                        WHERE table_type = 'BASE TABLE' and
                              table_schema = 'public' and
                              table_name not in ('spatial_ref_sys', 'alembic_version')
                        """))
            async for row in tables:
                resp['tables'].append(row[0])
            print(resp)
        return JSONResponse(resp)

    async def post(self, request: Request):
        engine = request.app.state.postgres
        param = await request.json()
        s = """GRANT ALL PRIVILEGES
        ON"""
        for i in param['tables']:
            s += ' {},'.format(i)
        s = s[:-1]+'\n        TO'
        for i in param['roles']:
            s += ' {},'.format(i)
        s = s[:-1]+';'
        async with engine.connect() as conn:
            await conn.stream(
                text(s))
        print(s)

        return JSONResponse('ok')


routes = [
    Route('/merging', endpoint=Merging),
    Route('/giverole', endpoint=Roler),
]
