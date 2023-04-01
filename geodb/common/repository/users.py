from time import time
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from psycopg2 import sql
from psycopg2 import sql

from sqlalchemy import text, insert, bindparam
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession


async def create_db_user(conn: AsyncConnection, username: str, password: str):

    SQL = """CREATE USER {} """.format(username)+"""WITH PASSWORD '{}'""".format(password)
    await conn.stream(text(SQL))
