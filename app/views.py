from aiohttp import web
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from models import User, Advert
from datetime import datetime
from auth import login_required, check_password
from schemas import UserCreate, UserUpdate, AdvertCreate, AdvertUpdate


class LoginView(web.View):
    async def post(self):
        data = await self.request.json()
        email = data.get('email')
        password = data.get('password')

        async with self.request.app['db'] as session:
            user = await check_password(session, email, password)
            if user:
                self.request['user'] = user
                return web.json_response({"status": "success", "user_id": user.id})
        return web.json_response({"status": "fail", "error": "Invalid email or password"}, status=401)


class UserView(web.View):
    @login_required
    async def get(self):
        user_id = int(self.request.match_info['user_id'])
        async with self.request.app['db'] as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return web.json_response(user.to_dict())
        return web.json_response({"error": "User not found"}, status=404)

    async def post(self):
        data = await self.request.json()
        user_data = UserCreate(**data)
        hashed = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt())
        user = User(name=user_data.name, email=user_data.email, password=hashed.decode())
        async with self.request.app['db'] as session:
            session.add(user)
            try:
                await session.commit()
                return web.json_response(user.to_dict(), status=201)
            except IntegrityError as e:
                await session.rollback()
                if "users_email_key" in str(e):
                    return web.json_response({"error": "Email already exists"}, status=400)
                return web.json_response({"error": "An error occurred while creating the user"}, status=500)

    @login_required
    async def patch(self):
        user_id = int(self.request.match_info['user_id'])
        data = await self.request.json()
        user_data = UserUpdate(**data)
        async with self.request.app['db'] as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                for key, value in user_data.dict(exclude_unset=True).items():
                    if key == 'password':
                        value = bcrypt.hashpw(value.encode(), bcrypt.gensalt()).decode()
                    setattr(user, key, value)
                await session.commit()
                return web.json_response(user.to_dict())
        return web.json_response({"error": "User not found"}, status=404)

    @login_required
    async def delete(self):
        user_id = int(self.request.match_info['user_id'])
        async with self.request.app['db'] as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                await session.delete(user)
                await session.commit()
                return web.json_response({"status": "success"})
        return web.json_response({"error": "User not found"}, status=404)


class AdvertView(web.View):
    @login_required
    async def get(self):
        advert_id = int(self.request.match_info['advert_id'])
        async with self.request.app['db'] as session:
            result = await session.execute(select(Advert).where(Advert.id == advert_id))
            advert = result.scalar_one_or_none()
            if advert:
                return web.json_response(advert.to_dict())
        return web.json_response({"error": "Advert not found"}, status=404)

    @login_required
    async def post(self):
        data = await self.request.json()
        advert_data = AdvertCreate(**data)
        async with self.request.app['db'] as session:
            user = await session.get(User, advert_data.owner_id)
            if not user:
                return web.json_response({"error": "User not found"}, status=404)

            advert = Advert(title=advert_data.title, description=advert_data.description,
                            creation_date=datetime.now(), owner_id=advert_data.owner_id)
            session.add(advert)
            await session.commit()
        return web.json_response(advert.to_dict(), status=201)

    @login_required
    async def patch(self):
        advert_id = int(self.request.match_info['advert_id'])
        data = await self.request.json()
        advert_data = AdvertUpdate(**data)
        async with self.request.app['db'] as session:
            result = await session.execute(select(Advert).where(Advert.id == advert_id))
            advert = result.scalar_one_or_none()
            if advert:
                for key, value in advert_data.dict(exclude_unset=True).items():
                    setattr(advert, key, value)
                await session.commit()
                return web.json_response(advert.to_dict())
        return web.json_response({"error": "Advert not found"}, status=404)

    @login_required
    async def delete(self):
        advert_id = int(self.request.match_info['advert_id'])
        async with self.request.app['db'] as session:
            result = await session.execute(select(Advert).where(Advert.id == advert_id))
            advert = result.scalar_one_or_none()
            if advert:
                await session.delete(advert)
                await session.commit()
                return web.json_response({"status": "success"})
        return web.json_response({"error": "Advert not found"}, status=404)