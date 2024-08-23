from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
from views import LoginView, UserView, AdvertView
from config import config


async def init_db(app):
    engine = create_async_engine(config['DATABASE_URL'], echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    app['db'] = async_session()

    yield

    await app['db'].close()


async def health_check(request):
    return web.json_response({"status": "ok"})


async def init_app():
    app = web.Application()
    app.cleanup_ctx.append(init_db)

    app.router.add_routes([
        web.get('/health', health_check),
        web.post('/login', LoginView),
        web.get('/user/{user_id}', UserView),
        web.post('/user', UserView),
        web.patch('/user/{user_id}', UserView),
        web.delete('/user/{user_id}', UserView),
        web.get('/advert/{advert_id}', AdvertView),
        web.post('/advert', AdvertView),
        web.patch('/advert/{advert_id}', AdvertView),
        web.delete('/advert/{advert_id}', AdvertView),
    ])

    return app


if __name__ == '__main__':
    app = init_app()
    web.run_app(app)
