from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse


async def test(request):
    return JSONResponse('OK')
