from contextlib import asynccontextmanager, contextmanager
from starlette.requests import Request
import logging
from starlette.exceptions import HTTPException
import typing as t


@asynccontextmanager
async def JsonParams(request: Request):
    """ Helps to use parameters received in JSON body.
    """
    try:
        params = await request.json()
        yield params
    except (AttributeError, KeyError, ValueError) as exc:
        msg = f"Bad request parameters. {exc}"
        if logging.root.isEnabledFor(logging.DEBUG):
            logging.exception(msg)
        else:
            logging.warning(msg)
        raise HTTPException(400, msg)


@contextmanager
def QueryParams(request: Request):
    """ Helps to use query parameters.
    """
    try:
        yield request.query_params._dict
    except (TypeError, AttributeError, KeyError) as exc:
        msg = f"Bad request parameters. {exc}"
        if logging.root.isEnabledFor(logging.DEBUG):
            logging.exception(msg)
        else:
            logging.warning(msg)
        raise HTTPException(400, msg)


class Result(dict):

    def __init__(self, *, columns: []):
        super().__init__({'columns': list(columns), 'rows': []})

    @property
    def rows(self) -> t.List[t.Sequence[t.Any]]:
        return self['rows']

    @property
    def columns(self) -> t.Sequence[str]:
        return self['columns']

