from aiohttp import web
from errors import CustomHTTPException


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except CustomHTTPException as e:
        return web.json_response({'error': str(e)}, status=e.status_code)
    except Exception as e:
        return web.json_response({'error': 'Internal server error'}, status=500)


@web.middleware
async def db_session_middleware(request, handler):
    async with request.app['db_session']() as session:
        request['db_session'] = session
        response = await handler(request)
        return response