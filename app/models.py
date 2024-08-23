from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import config

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    adverts = relationship("Advert", back_populates="owner")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }


class Advert(Base):
    __tablename__ = 'adverts'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    creation_date = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="adverts")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'creation_date': self.creation_date.isoformat(),
            'owner_id': self.owner_id
        }


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