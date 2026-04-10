import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)

AsyncSessionFactory = async_sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

async def get_async_session():
    async with AsyncSessionFactory() as session:
        yield session





