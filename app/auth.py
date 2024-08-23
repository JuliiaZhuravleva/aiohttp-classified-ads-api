from aiohttp import web
from sqlalchemy import select
from models import User
import bcrypt
from functools import wraps


async def check_password(session, email, password):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user and bcrypt.checkpw(password.encode(), user.password.encode()):
        return user
    return None


def login_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        request = self.request
        auth = request.headers.get('Authorization')
        if not auth:
            return web.json_response({"error": "Authorization required"}, status=401)

        email, password = auth.split(':')
        async with request.app['db'] as session:
            user = await check_password(session, email, password)
            if not user:
                return web.json_response({"error": "Invalid credentials"}, status=401)

            request['user'] = user
            return await func(self, *args, **kwargs)

    return wrapper