from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime, Table, Column, ForeignKey, func, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from common.models.bases import metadata, mapper_registry


@dataclass
class User:
    """ Пользователь (Профиль пользователя)
    """
    id: int = field(init=False)
    email: str = None
    username: str = None
    password: str = None
    right: 'Right' = None
    created_at: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
    disabled_at: datetime = None


@dataclass
class Right:
    """ Таблица прав пользователей
    """
    right: str
    description: str = None


users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String),
    Column('username', String),
    Column('password', String),
    Column('created_at', DateTime, nullable=False, server_default=func.now()),
    Column('disabled_at', DateTime),
)

rights = Table(
    'rights',
    metadata,
    Column('name', String, primary_key=True),
    Column('description', String),
)

user_rights = Table(
    'user_rights',
    metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('right', String, ForeignKey('rights.name')),
    PrimaryKeyConstraint('user_id', 'right', name='primary_user_rights'),
)

mapper_registry.map_imperatively(User, users, properties={
   'rights': relationship(Right, secondary=user_rights, back_populates="users", uselist=False),
})

mapper_registry.map_imperatively(Right, rights, properties={
   'users': relationship(User, secondary=user_rights, back_populates="rights"),
})