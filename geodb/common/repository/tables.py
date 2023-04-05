import decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.responses import JSONResponse

from website.utils import Result


async def get_users_table(conn: AsyncConnection, current_user: str):
    SQL = """
    select nsp.nspname as object_schema,
      cls.relname as object_name,
      rol.rolname as owner
    from pg_class cls
      join pg_roles rol on rol.oid = cls.relowner
      join pg_namespace nsp on nsp.oid = cls.relnamespace
    where nsp.nspname not in ('information_schema', 'pg_catalog', 'tiger', 'topology')
      and nsp.nspname not like 'pg_toast%'
      and cls.relkind like ('r')
      and rol.rolname = :current_user
    order by nsp.nspname, cls.relname;
    """
    users_tables = await conn.stream(text(SQL).bindparams(current_user=current_user))
    tables_list = []
    async for table_info in users_tables:
        SQL = """SELECT * FROM {}""".format(table_info[1])
        data = await conn.stream(text(SQL))
        result = Result(
            columns=({'field': col, 'headerName': col, 'width': 150, 'editable': True} for col in tuple(data.keys())))
        async for row in data:
            result.rows.append({key['field']: float(row._asdict()[key['field']]) if type(
                row._asdict()[key['field']]) == decimal.Decimal else row._asdict()[key['field']] for key in
                                result.columns})
        tables_list.append(result)
    return tables_list
