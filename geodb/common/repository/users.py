from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def create_db_user(conn: AsyncConnection, username: str, password: str):

    SQL = """CREATE USER {} """.format(username)+"""WITH PASSWORD '{}'""".format(password)
    await conn.stream(text(SQL))
