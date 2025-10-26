from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config
from src.books.models import Book
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

async_engine = AsyncEngine(
  create_engine(
  url=Config.DATABASE_URL,
  echo=True
))

async def init_db():
  async with async_engine.begin() as conn:
    from src.books.models import Book

    await conn.run_sync(SQLModel.metadata.create_all)


async def get_session()->AsyncSession:
  Session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
  )
  async with Session() as session:
    yield session

# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from typing import AsyncGenerator
# from sqlmodel import SQLModel

# from src.config import Config

# async_engine = create_async_engine(
#     url=Config.DATABASE_URL,
#     echo=True
# )

# async def init_db():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)

# async def get_session() -> AsyncGenerator[AsyncSession, None]:
#     async_session = async_sessionmaker(
#         bind=async_engine, class_=AsyncSession, expire_on_commit=False
#     )

#     async with async_session() as session:
#         yield session