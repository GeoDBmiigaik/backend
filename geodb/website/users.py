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
from common.repository.users import create_db_user
from website.utils import JsonParams


@dataclass
class SessionUser:
    id: int
    display_name: str = None
    credentials: [str] = field(default_factory=list)


class AuthenticatedUser(SessionUser, BaseUser):

    @property
    def is_authenticated(self):
        return True

    @property
    def identity(self):
        return '{:016}'.format(self.id)


class AuthBackend(AuthenticationBackend):

    async def authenticate(self, conn):
        user = UnauthenticatedUser()
        credentials = ['anonymous']
        session_user = conn.session.get('user', None)
        if session_user is not None:
            user = AuthenticatedUser(**session_user)
            credentials = list(set(user.credentials + ['authenticated']))
        return AuthCredentials(credentials), user


class Session(HTTPEndpoint):
    """ Обработка запросов на получение и управление текущей сессией
    """

    async def set_session_user(self, request, user_id):
        engine = request.app.state.postgres  # type: AsyncEngine
        async with AsyncSession(engine) as session:
            user = (
                await session.execute(select(User).filter_by(id=user_id).options(selectinload(User.rights)))).scalar()
            if user and user.disabled_at is None:
                rights = (await session.execute(select(user_rights).filter_by(user_id=user.id)))
                request.session['user'] = asdict(
                    SessionUser(
                        id=user.id,
                        display_name=f'{user.username or ""} '.strip() or None,
                        credentials=[row[1] for row in rights]
                    ))
                return True
        return False

    async def get(self, request: Request):
        if request.user.is_authenticated:
            request.session.pop('user', None)
            await self.set_session_user(request, request.user.id)
        print(request.session['user'])
        return JSONResponse(request.session)

    @requires('authenticated')
    async def delete(self, request: Request):
        request.session.pop('user', None)
        return Response(status_code=200)


class Registration(HTTPEndpoint):

    async def post(self, request: Request):
        engine = request.app.state.postgres  # type: AsyncEngine
        async with JsonParams(request) as param:
            email = param.get('email')
            username = param.get('username')
            password = param.get('password')
        async with AsyncSession(engine) as session:
            account = (await session.execute(select(User)
                                             .where(or_(User.username == username, User.email == email))
                                             .options(selectinload(User.rights))
                                             )).scalar()
            if account:
                raise HTTPException(403)

            account = User(email, username, password)
            right = Right(username, '{} right'.format(username))
            right2 = Right('{} new right'.format(username), '{} right'.format(username))
            account.rights = [right, right2]
            session.add_all([right, right2])
            session.add(account)
            await Session.set_session_user(self, request, account.id)
            await session.commit()
        async with engine.connect() as conn:
            await create_db_user(conn, username=username, password=password)
            await conn.commit()
        return Response(status_code=200)


class Authentication(HTTPEndpoint):

    async def post(self, request: Request):
        engine = request.app.state.postgres  # type: AsyncEngine
        async with JsonParams(request) as param:
            username = param.get('username')
            password = param.get('password')
        async with AsyncSession(engine) as session:
            user = (await session.execute(select(User)
                                          .filter_by(username=username, password=password)
                                          .options(selectinload(User.rights))
                                          )).scalar()
            if user is None or user.disabled_at:
                raise HTTPException(403)
            await Session.set_session_user(self, request, user.id)
        return Response(status_code=200)

    @requires('authenticated')
    async def delete(self, request: Request):
        return await Session.delete(self, request)


routes = [
    Route('/signup', endpoint=Registration),
    Route('/session', endpoint=Session),
    Route('/signin', endpoint=Authentication)
]
